"""
Chunking strategies.

- RecursiveChunker: splits on a hierarchy of separators (paragraphs ->
  lines -> sentences -> words) trying to keep chunks close to a target
  size with overlap, without ever cutting mid-word. Fast, deterministic,
  good default for most documents.

- SemanticChunker: splits at sentence boundaries where embedding
  similarity between consecutive sentences drops sharply — i.e. where
  the topic actually shifts — producing more coherent chunks at the
  cost of an embedding pass over sentences. Used when higher answer
  quality matters more than ingestion speed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.config import settings

_SEPARATOR_HIERARCHY = ["\n\n", "\n", ". ", " "]

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    text: str
    index: int
    page_number: int | None = None


def _approx_token_count(text: str) -> int:
    # Cheap approximation (~4 chars/token for English) — avoids pulling in
    # a tokenizer just for chunk sizing decisions.
    return max(1, len(text) // 4)


class RecursiveChunker:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split(self, text: str, separators: list[str]) -> list[str]:
        if not separators:
            return [text]

        sep, *rest = separators
        parts = [p for p in text.split(sep) if p.strip()]

        pieces: list[str] = []
        for part in parts:
            if _approx_token_count(part) <= self.chunk_size:
                pieces.append(part)
            else:
                pieces.extend(self._split(part, rest))
        return pieces

    def chunk(self, text: str, page_number: int | None = None) -> list[Chunk]:
        text = text.strip()
        if not text:
            return []

        pieces = self._split(text, _SEPARATOR_HIERARCHY)

        merged: list[str] = []
        buffer = ""
        for piece in pieces:
            candidate = f"{buffer} {piece}".strip() if buffer else piece
            if _approx_token_count(candidate) <= self.chunk_size:
                buffer = candidate
            else:
                if buffer:
                    merged.append(buffer)
                buffer = piece
        if buffer:
            merged.append(buffer)

        # Apply overlap by prepending the tail of the previous chunk.
        overlapped: list[str] = []
        for i, chunk_text in enumerate(merged):
            if i == 0 or self.chunk_overlap <= 0:
                overlapped.append(chunk_text)
                continue
            prev = merged[i - 1]
            overlap_chars = self.chunk_overlap * 4
            tail = prev[-overlap_chars:]
            overlapped.append(f"{tail} {chunk_text}".strip())

        return [
            Chunk(text=c, index=i, page_number=page_number)
            for i, c in enumerate(overlapped)
            if c.strip()
        ]


class SemanticChunker:
    """
    Groups consecutive sentences into a chunk until embedding similarity
    to the running chunk centroid drops below `similarity_threshold`,
    signaling a topic shift, or the size cap is hit.
    """

    def __init__(
        self,
        embed_fn,
        similarity_threshold: float = 0.55,
        max_chunk_size: int = settings.CHUNK_SIZE,
    ) -> None:
        self._embed_fn = embed_fn  # Callable[[list[str]], list[list[float]]]
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def chunk(self, text: str, page_number: int | None = None) -> list[Chunk]:
        sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
        if not sentences:
            return []
        if len(sentences) == 1:
            return [Chunk(text=sentences[0], index=0, page_number=page_number)]

        embeddings = self._embed_fn(sentences)

        chunks: list[Chunk] = []
        current_sentences = [sentences[0]]
        current_embedding = embeddings[0]
        chunk_index = 0

        for sentence, embedding in zip(sentences[1:], embeddings[1:]):
            similarity = self._cosine_similarity(current_embedding, embedding)
            candidate_text = " ".join(current_sentences + [sentence])

            if similarity < self.similarity_threshold or _approx_token_count(candidate_text) > self.max_chunk_size:
                chunks.append(
                    Chunk(text=" ".join(current_sentences), index=chunk_index, page_number=page_number)
                )
                chunk_index += 1
                current_sentences = [sentence]
                current_embedding = embedding
            else:
                current_sentences.append(sentence)
                # Running centroid: cheap incremental average.
                current_embedding = [
                    (a * (len(current_sentences) - 1) + b) / len(current_sentences)
                    for a, b in zip(current_embedding, embedding)
                ]

        if current_sentences:
            chunks.append(
                Chunk(text=" ".join(current_sentences), index=chunk_index, page_number=page_number)
            )

        return chunks
