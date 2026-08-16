"""
Ingestion pipeline — turns raw uploaded bytes into searchable chunks.

Flow: parse -> chunk each page -> embed all chunks -> write vectors to
FAISS -> build BM25 index -> return DocumentChunk rows ready to persist.

This module has no DB or FastAPI imports — it's pure transformation
logic, which keeps it independently unit-testable and reusable from a
background worker if ingestion is later moved off the request path.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.ingestion.chunking import RecursiveChunker
from app.ingestion.parsers import ParsingError, extract_document_metadata, parse_document
from app.models.document import DocumentType
from app.retrieval.bm25_index import BM25Index
from app.retrieval.embeddings import EmbeddingProvider
from app.retrieval.vector_store import VectorStore


@dataclass
class IngestedChunk:
    chunk_index: int
    content: str
    page_number: int | None
    token_count: int
    vector_id: int
    metadata: dict


class IngestionError(Exception):
    """Raised when ingestion fails at any stage of the pipeline."""


def run_ingestion_pipeline(
    document_id: uuid.UUID,
    file_bytes: bytes,
    document_type: DocumentType,
    embedding_provider: EmbeddingProvider,
    chunker: RecursiveChunker | None = None,
) -> list[IngestedChunk]:
    chunker = chunker or RecursiveChunker()

    try:
        pages = parse_document(file_bytes, document_type)
    except ParsingError as exc:
        raise IngestionError(f"Parsing failed: {exc}") from exc

    doc_metadata = extract_document_metadata(file_bytes, document_type)
    base_metadata = {
        k: v
        for k, v in {
            "title": doc_metadata.title,
            "author": doc_metadata.author,
            "source_created_at": doc_metadata.created_at,
        }.items()
        if v is not None
    }

    all_chunks = []
    for page in pages:
        if not page.text.strip():
            continue
        page_chunks = chunker.chunk(page.text, page_number=page.page_number)
        all_chunks.extend(page_chunks)

    if not all_chunks:
        raise IngestionError("Document contained no extractable text")

    texts = [c.text for c in all_chunks]

    try:
        vectors = embedding_provider.embed_documents(texts)
    except Exception as exc:  # noqa: BLE001
        raise IngestionError(f"Embedding generation failed: {exc}") from exc

    vector_store = VectorStore(document_id=document_id, dimension=embedding_provider.dimension)
    vector_ids = vector_store.add(vectors)
    vector_store.persist()

    bm25_index = BM25Index(document_id=document_id)
    bm25_index.build(texts=texts, vector_ids=vector_ids)
    bm25_index.persist()

    ingested: list[IngestedChunk] = []
    for i, (chunk, vector_id) in enumerate(zip(all_chunks, vector_ids)):
        ingested.append(
            IngestedChunk(
                chunk_index=i,
                content=chunk.text,
                page_number=chunk.page_number,
                token_count=max(1, len(chunk.text) // 4),
                vector_id=vector_id,
                metadata=dict(base_metadata),
            )
        )

    return ingested
