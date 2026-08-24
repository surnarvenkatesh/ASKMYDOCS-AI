"""
Hybrid retriever — the core of the "BM25 * Vector -> RRF -> Cross-Encoder
-> Top Context" pipeline described in the product spec.

Retrieval happens per-document (each document has its own FAISS/BM25
index), producing candidate keys of the form (document_id, vector_id).
Those per-document rankings are fused globally with Reciprocal Rank
Fusion, then the surviving top candidates are re-scored jointly against
the query with a cross-encoder before being resolved back to their
DocumentChunk rows for prompt-building and citation.
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.chunk import DocumentChunk
from app.retrieval.bm25_index import BM25Index
from app.retrieval.embeddings import EmbeddingProvider
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.reranker import rerank
from app.retrieval.vector_store import VectorStore

CandidateKey = tuple[uuid.UUID, int]  # (document_id, vector_id)


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    document_filename: str
    confidence_score: float


class HybridRetriever:
    def __init__(self, db: AsyncSession, embedding_provider: EmbeddingProvider) -> None:
        self._db = db
        self._embeddings = embedding_provider

    async def _ensure_indexes_built(self, document_id: uuid.UUID) -> None:
        """Rebuild the on-disk FAISS/BM25 indexes from Postgres if they're
        missing — e.g. after a container restart on ephemeral storage,
        where the index files never survive but chunk text does."""
        from pathlib import Path

        index_dir = Path(settings.VECTOR_STORE_PATH) / str(document_id)
        faiss_path = index_dir / "index.faiss"
        bm25_path = index_dir / "bm25.pkl"

        if faiss_path.exists() and bm25_path.exists():
            return

        result = await self._db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        chunks = result.scalars().all()
        if not chunks:
            return

        texts = [c.content for c in chunks]
        vectors = self._embeddings.embed_documents(texts)

        vector_store = VectorStore(document_id, dimension=self._embeddings.dimension)
        vector_ids = vector_store.add(vectors)
        vector_store.persist()

        bm25_index = BM25Index(document_id)
        bm25_index.build(texts, vector_ids)
        bm25_index.persist()

    async def retrieve(
        self,
        query: str,
        document_ids: list[uuid.UUID],
        top_k: int = settings.RERANK_TOP_K,
    ) -> list[RetrievedChunk]:
        if not document_ids:
            return []

        bm25_ranked: list[CandidateKey] = []
        vector_ranked: list[CandidateKey] = []

        query_embedding = self._embeddings.embed_query(query)

        for document_id in document_ids:
            await self._ensure_indexes_built(document_id)

            bm25_hits = BM25Index(document_id).search(query, top_k=settings.BM25_TOP_K)
            bm25_ranked.extend((document_id, vid) for vid, _ in bm25_hits)

            vector_store = VectorStore(document_id, dimension=self._embeddings.dimension)
            vector_hits = vector_store.search(query_embedding, top_k=settings.VECTOR_TOP_K)
            vector_ranked.extend((document_id, vid) for vid, _ in vector_hits)

        # Interleave each method's per-document results by relative rank
        # so the global fused list still reflects "best of each method"
        # across documents (rather than one document dominating because
        # it happened to be processed first).
        bm25_ranked = _reorder_by_relative_rank(bm25_ranked)
        vector_ranked = _reorder_by_relative_rank(vector_ranked)

        fused = reciprocal_rank_fusion([bm25_ranked, vector_ranked], k=settings.RRF_K)
        if not fused:
            return []

        # Only pull chunk text for a bounded candidate pool before the
        # (hosted, API-based) rerank pass.
        candidate_keys = [key for key, _ in fused[: max(top_k * 4, 20)]]
        chunks_by_key = await self._load_chunks(candidate_keys)

        candidates = [
            (key, chunks_by_key[key].content)
            for key in candidate_keys
            if key in chunks_by_key
        ]

        reranked = await asyncio.to_thread(
            rerank, query, [(i, text) for i, (_, text) in enumerate(candidates)], top_k=top_k
        )

        results: list[RetrievedChunk] = []
        for local_idx, _text, score in reranked:
            key = candidates[local_idx][0]
            chunk = chunks_by_key[key]
            results.append(
                RetrievedChunk(
                    chunk=chunk,
                    document_filename=chunk.document.filename if chunk.document else "",
                    confidence_score=_normalize_score(score),
                )
            )
        return results

    async def _load_chunks(self, keys: list[CandidateKey]) -> dict[CandidateKey, DocumentChunk]:
        if not keys:
            return {}
        document_ids = {doc_id for doc_id, _ in keys}
        result = await self._db.execute(
            select(DocumentChunk)
            .options(selectinload(DocumentChunk.document))
            .where(DocumentChunk.document_id.in_(document_ids))
        )
        rows = result.scalars().all()
        by_key = {(row.document_id, row.vector_id): row for row in rows}
        return {key: by_key[key] for key in keys if key in by_key}


def _reorder_by_relative_rank(items: list[CandidateKey]) -> list[CandidateKey]:
    """Items were appended per-document in original per-document rank
    order; re-sort so rank-1-across-all-documents comes first, then
    rank-2-across-all-documents, etc. Cheap fairness fix for RRF fusion
    across multiple per-document candidate lists of uneven length."""
    grouped: dict[uuid.UUID, list[CandidateKey]] = {}
    for key in items:
        grouped.setdefault(key[0], []).append(key)

    interleaved: list[CandidateKey] = []
    max_len = max((len(v) for v in grouped.values()), default=0)
    for i in range(max_len):
        for doc_items in grouped.values():
            if i < len(doc_items):
                interleaved.append(doc_items[i])
    return interleaved


def _normalize_score(raw_score: float) -> float:
    """Cohere's rerank relevance_score is already a (0, 1) probability —
    just clamp defensively in case of any edge-case values."""
    return max(0.0, min(1.0, raw_score))
