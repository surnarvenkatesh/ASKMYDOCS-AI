"""
Unit tests for app.ingestion.pipeline.run_ingestion_pipeline.

Uses a FakeEmbeddingProvider so the test suite never downloads a real
sentence-transformers model, and points VECTOR_STORE_PATH at a temp dir
so FAISS/BM25 artifacts don't pollute the repo.
"""
import uuid

import pytest

from app.ingestion.chunking import RecursiveChunker
from app.ingestion.pipeline import IngestionError, run_ingestion_pipeline
from app.models.document import DocumentType
from app.retrieval.embeddings import EmbeddingProvider


class FakeEmbeddingProvider(EmbeddingProvider):
    """Deterministic, dependency-free stand-in for a real embedder."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # 4-dim hash-based vector, deterministic per text.
        return [[float((hash(t) >> (8 * i)) % 100) for i in range(4)] for t in texts]

    @property
    def dimension(self) -> int:
        return 4


@pytest.fixture(autouse=True)
def _isolated_vector_store(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "VECTOR_STORE_PATH", str(tmp_path))
    yield


@pytest.mark.unit
class TestRunIngestionPipeline:
    def test_ingests_plain_text_into_chunks(self):
        document_id = uuid.uuid4()
        text = "This is sentence one. This is sentence two. This is sentence three."
        chunks = run_ingestion_pipeline(
            document_id=document_id,
            file_bytes=text.encode("utf-8"),
            document_type=DocumentType.TXT,
            embedding_provider=FakeEmbeddingProvider(),
            chunker=RecursiveChunker(chunk_size=10, chunk_overlap=2),
        )
        assert len(chunks) > 0
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert chunk.content.strip()
            assert chunk.vector_id == i  # first document -> vector ids start at 0

    def test_empty_document_raises_ingestion_error(self):
        with pytest.raises(IngestionError, match="no extractable text"):
            run_ingestion_pipeline(
                document_id=uuid.uuid4(),
                file_bytes=b"   \n\n   ",
                document_type=DocumentType.TXT,
                embedding_provider=FakeEmbeddingProvider(),
            )

    def test_corrupt_docx_raises_ingestion_error(self):
        with pytest.raises(IngestionError, match="Parsing failed"):
            run_ingestion_pipeline(
                document_id=uuid.uuid4(),
                file_bytes=b"not a real docx",
                document_type=DocumentType.DOCX,
                embedding_provider=FakeEmbeddingProvider(),
            )

    def test_markdown_round_trip(self):
        document_id = uuid.uuid4()
        md_text = "# Heading\n\nSome content here that is reasonably long for chunking purposes."
        chunks = run_ingestion_pipeline(
            document_id=document_id,
            file_bytes=md_text.encode("utf-8"),
            document_type=DocumentType.MARKDOWN,
            embedding_provider=FakeEmbeddingProvider(),
        )
        assert len(chunks) >= 1
        assert "Heading" in chunks[0].content
