"""
Unit tests for app.ingestion.chunking.
"""
import pytest

from app.ingestion.chunking import RecursiveChunker, SemanticChunker


@pytest.mark.unit
class TestRecursiveChunker:
    def test_empty_text_returns_no_chunks(self):
        chunker = RecursiveChunker(chunk_size=100, chunk_overlap=10)
        assert chunker.chunk("") == []
        assert chunker.chunk("   ") == []

    def test_short_text_returns_single_chunk(self):
        chunker = RecursiveChunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.chunk("This is a short sentence.")
        assert len(chunks) == 1
        assert chunks[0].text == "This is a short sentence."

    def test_long_text_splits_into_multiple_chunks(self):
        chunker = RecursiveChunker(chunk_size=20, chunk_overlap=5)
        paragraph = " ".join([f"word{i}" for i in range(200)])
        chunks = chunker.chunk(paragraph)
        assert len(chunks) > 1
        for c in chunks:
            assert c.text.strip()

    def test_chunk_indices_are_sequential(self):
        chunker = RecursiveChunker(chunk_size=20, chunk_overlap=5)
        paragraph = " ".join([f"word{i}" for i in range(100)])
        chunks = chunker.chunk(paragraph)
        assert [c.index for c in chunks] == list(range(len(chunks)))

    def test_page_number_propagates_to_all_chunks(self):
        chunker = RecursiveChunker(chunk_size=20, chunk_overlap=5)
        paragraph = " ".join([f"word{i}" for i in range(60)])
        chunks = chunker.chunk(paragraph, page_number=7)
        assert all(c.page_number == 7 for c in chunks)

    def test_paragraph_boundaries_respected_when_possible(self):
        chunker = RecursiveChunker(chunk_size=500, chunk_overlap=0)
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunks = chunker.chunk(text)
        assert len(chunks) == 1  # fits within chunk_size, no need to split


@pytest.mark.unit
class TestSemanticChunker:
    @staticmethod
    def fake_embed(sentences: list[str]) -> list[list[float]]:
        # Deterministic fake: sentences containing "cat" cluster near
        # [1, 0], sentences containing "car" cluster near [0, 1].
        vectors = []
        for s in sentences:
            if "cat" in s.lower():
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return vectors

    def test_single_sentence_returns_single_chunk(self):
        chunker = SemanticChunker(embed_fn=self.fake_embed)
        chunks = chunker.chunk("Only one sentence here.")
        assert len(chunks) == 1

    def test_topic_shift_creates_new_chunk(self):
        chunker = SemanticChunker(embed_fn=self.fake_embed, similarity_threshold=0.5)
        text = "I have a cat. My cat is fluffy. I bought a car. The car is fast."
        chunks = chunker.chunk(text)
        # Expect roughly two topic clusters (cat.. / car..)
        assert len(chunks) >= 2

    def test_empty_text_returns_no_chunks(self):
        chunker = SemanticChunker(embed_fn=self.fake_embed)
        assert chunker.chunk("") == []
