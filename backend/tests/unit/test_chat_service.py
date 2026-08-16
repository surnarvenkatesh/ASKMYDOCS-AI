"""
Unit tests for app.services.chat_service.ChatService, fully faked out
(no DB, no real retrieval, no real LLM) to exercise the orchestration
logic in isolation.
"""
import uuid
from dataclasses import dataclass

import pytest

from app.models.conversation import MessageRole
from app.retrieval.llm_provider import LLMProvider
from app.services.chat_service import ChatService


@dataclass
class FakeChunk:
    id: uuid.UUID
    content: str
    page_number: int | None


@dataclass
class FakeRetrievedChunk:
    chunk: FakeChunk
    document_filename: str
    confidence_score: float


class FakeRetriever:
    def __init__(self, results):
        self._results = results

    async def retrieve(self, query, document_ids, top_k=5):
        return self._results


class FakeLLM(LLMProvider):
    def __init__(self, tokens: list[str]):
        self._tokens = tokens

    async def stream(self, system_prompt, user_prompt):
        for token in self._tokens:
            yield token


class FakeDocumentRepo:
    def __init__(self, document_ids):
        self._ids = document_ids

    async def get_by_id(self, doc_id, owner_id):
        class Doc:
            id = doc_id

        return Doc() if doc_id in self._ids else None

    async def list_for_owner(self, owner_id, search, limit, offset):
        class Doc:
            def __init__(self, id_):
                self.id = id_

        return [Doc(i) for i in self._ids], len(self._ids)


class FakeConversationRepo:
    def __init__(self):
        self.messages = []

    async def add_message(self, conversation_id, role, content, citations=None, generation_metadata=None):
        self.messages.append((role, content, citations or [], generation_metadata or {}))


def _make_retrieved_chunk(ref_content: str, filename: str = "doc.pdf", page: int = 1):
    return FakeRetrievedChunk(
        chunk=FakeChunk(id=uuid.uuid4(), content=ref_content, page_number=page),
        document_filename=filename,
        confidence_score=0.8,
    )


@pytest.mark.unit
class TestAnswerStream:
    async def test_no_documents_yields_error(self):
        doc_repo = FakeDocumentRepo(document_ids=[])
        service = ChatService(
            FakeConversationRepo(), doc_repo, FakeRetriever([]), FakeLLM(["hi"])
        )
        events = [
            e
            async for e in service.answer_stream(
                owner_id=uuid.uuid4(), conversation_id=uuid.uuid4(), question="What?", document_ids=None
            )
        ]
        assert events[0].type == "error"
        assert "upload a document" in events[0].text.lower()

    async def test_no_retrieved_chunks_yields_error(self):
        doc_id = uuid.uuid4()
        doc_repo = FakeDocumentRepo(document_ids=[doc_id])
        service = ChatService(
            FakeConversationRepo(), doc_repo, FakeRetriever([]), FakeLLM(["hi"])
        )
        events = [
            e
            async for e in service.answer_stream(
                owner_id=uuid.uuid4(), conversation_id=uuid.uuid4(), question="What?", document_ids=None
            )
        ]
        assert events[0].type == "error"
        assert "couldn't find" in events[0].text.lower()

    async def test_successful_answer_streams_tokens_then_citations_then_done(self):
        doc_id = uuid.uuid4()
        doc_repo = FakeDocumentRepo(document_ids=[doc_id])
        retriever = FakeRetriever([_make_retrieved_chunk("Revenue grew 20% last quarter.")])
        llm = FakeLLM(["Revenue ", "grew ", "20% ", "[1]."])
        conv_repo = FakeConversationRepo()
        service = ChatService(conv_repo, doc_repo, retriever, llm)

        events = [
            e
            async for e in service.answer_stream(
                owner_id=uuid.uuid4(), conversation_id=uuid.uuid4(), question="How did revenue grow?", document_ids=None
            )
        ]

        token_events = [e for e in events if e.type == "token"]
        assert "".join(e.text for e in token_events) == "Revenue grew 20% [1]."

        citation_events = [e for e in events if e.type == "citations"]
        assert len(citation_events) == 1
        assert citation_events[0].citations[0]["document_filename"] == "doc.pdf"

        assert events[-1].type == "done"

        # Both the user question and the assistant answer were persisted.
        roles = [m[0] for m in conv_repo.messages]
        assert roles == [MessageRole.USER, MessageRole.ASSISTANT]

    async def test_unverifiable_answer_emits_warning(self):
        doc_id = uuid.uuid4()
        doc_repo = FakeDocumentRepo(document_ids=[doc_id])
        retriever = FakeRetriever([_make_retrieved_chunk("Some fact.")])
        # LLM answers with substantial prose but never cites anything.
        llm = FakeLLM(["This is a fairly long uncited claim about the data with no citation markers at all."])
        service = ChatService(FakeConversationRepo(), doc_repo, retriever, llm)

        events = [
            e
            async for e in service.answer_stream(
                owner_id=uuid.uuid4(), conversation_id=uuid.uuid4(), question="Explain", document_ids=None
            )
        ]
        assert any(e.type == "warning" for e in events)

    async def test_unknown_document_id_raises_before_streaming(self):
        doc_repo = FakeDocumentRepo(document_ids=[])
        service = ChatService(
            FakeConversationRepo(), doc_repo, FakeRetriever([]), FakeLLM(["hi"])
        )
        with pytest.raises(Exception):
            async for _ in service.answer_stream(
                owner_id=uuid.uuid4(),
                conversation_id=uuid.uuid4(),
                question="What?",
                document_ids=[uuid.uuid4()],
            ):
                pass
