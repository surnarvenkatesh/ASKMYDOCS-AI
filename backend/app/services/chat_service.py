"""
Chat service — the RAG orchestrator: hybrid retrieval -> prompt builder
-> LLM streaming -> citation validation -> persistence.

Exposes an async generator (`answer_stream`) so the API layer can push
tokens to the client via Server-Sent Events as they're generated,
followed by a final citations payload once the full answer is known.
"""
from __future__ import annotations

import time
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from app.core.config import settings
from app.models.conversation import MessageRole
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_repository import DocumentRepository
from app.retrieval.citation_validator import validate_citations
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.llm_provider import LLMProvider
from app.retrieval.prompt_builder import SYSTEM_PROMPT, ContextChunk, build_user_prompt
from app.utils.cost import estimate_cost_usd, estimate_tokens

OUT_OF_SCOPE_MESSAGE = (
    "This question is out of the scope of your uploaded documents. "
    "I couldn't find any relevant, sufficiently confident passages to answer it — "
    "try rephrasing, or upload a document that covers this topic."
)


class ChatServiceError(Exception):
    """Raised for user-facing chat failures (4xx-worthy)."""


@dataclass
class StreamEvent:
    type: str  # "token" | "citations" | "warning" | "done" | "error"
    text: str = ""
    citations: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class ChatService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        document_repository: DocumentRepository,
        retriever: HybridRetriever,
        llm: LLMProvider,
    ) -> None:
        self._conversations = conversation_repository
        self._documents = document_repository
        self._retriever = retriever
        self._llm = llm

    async def _resolve_document_scope(
        self, owner_id: uuid.UUID, document_ids: list[uuid.UUID] | None
    ) -> list[uuid.UUID]:
        if document_ids:
            resolved = []
            for doc_id in document_ids:
                doc = await self._documents.get_by_id(doc_id, owner_id=owner_id)
                if doc is None:
                    raise ChatServiceError(f"Document {doc_id} not found")
                resolved.append(doc.id)
            return resolved

        documents, _ = await self._documents.list_for_owner(owner_id, search=None, limit=1000, offset=0)
        return [d.id for d in documents]

    async def answer_stream(
        self,
        owner_id: uuid.UUID,
        conversation_id: uuid.UUID,
        question: str,
        document_ids: list[uuid.UUID] | None,
    ) -> AsyncIterator[StreamEvent]:
        started_at = time.perf_counter()

        scope = await self._resolve_document_scope(owner_id, document_ids)
        if not scope:
            yield StreamEvent(
                type="error",
                text="You don't have any indexed documents yet. Upload a document before asking a question.",
            )
            return

        retrieved = await self._retriever.retrieve(question, scope)
        retrieval_ms = int((time.perf_counter() - started_at) * 1000)

        if not retrieved:
            yield StreamEvent(type="error", text=OUT_OF_SCOPE_MESSAGE)
            return

        context_chunks = [
            ContextChunk(
                ref_id=i + 1,
                document_filename=r.document_filename,
                page_number=r.chunk.page_number,
                content=r.chunk.content,
            )
            for i, r in enumerate(retrieved)
        ]
        chunk_scores = {i + 1: r.confidence_score for i, r in enumerate(retrieved)}
        chunk_ids = {i + 1: str(r.chunk.id) for i, r in enumerate(retrieved)}

        await self._conversations.add_message(conversation_id, MessageRole.USER, question)

        user_prompt = build_user_prompt(question, context_chunks)

        generation_started_at = time.perf_counter()
        full_answer = ""
        async for token in self._llm.stream(SYSTEM_PROMPT, user_prompt):
            full_answer += token
            yield StreamEvent(type="token", text=token)
        generation_ms = int((time.perf_counter() - generation_started_at) * 1000)

        validation = validate_citations(full_answer, context_chunks, chunk_scores, chunk_ids)

        usable_citations = [
            c
            for c in validation.citations
            if c.confidence_score >= 0.0
        ]
        citation_dicts = [
            {
                "ref_id": c.ref_id,
                "document_filename": c.document_filename,
                "page_number": c.page_number,
                "chunk_id": c.chunk_id,
                "confidence_score": round(c.confidence_score, 4),
                "snippet": c.snippet,
            }
            for c in usable_citations
        ]

        metadata = {
            "retrieval_ms": retrieval_ms,
            "generation_ms": generation_ms,
            "chunks_considered": len(retrieved),
            "invalid_citation_refs": validation.invalid_ref_ids,
            "token_usage": {
                "prompt_tokens": estimate_tokens(SYSTEM_PROMPT) + estimate_tokens(user_prompt),
                "completion_tokens": estimate_tokens(full_answer),
            },
            "estimated_cost_usd": estimate_cost_usd(
                estimate_tokens(SYSTEM_PROMPT) + estimate_tokens(user_prompt),
                estimate_tokens(full_answer),
            ),
        }

        if validation.has_unverifiable_claims:
            yield StreamEvent(
                type="warning",
                text="This answer made claims without citing a source excerpt — treat it with extra caution.",
            )

        await self._conversations.add_message(
            conversation_id,
            MessageRole.ASSISTANT,
            full_answer,
            citations=citation_dicts,
            generation_metadata=metadata,
        )

        yield StreamEvent(type="citations", citations=citation_dicts, metadata=metadata)
        yield StreamEvent(type="done")
