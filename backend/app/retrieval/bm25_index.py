"""
BM25 keyword index wrapper.

Persisted as a pickled (tokenized-corpus, chunk_ids) pair per document
next to the FAISS index, so hybrid retrieval can rebuild either side
independently without re-parsing the source document.
"""
from __future__ import annotations

import pickle
import re
import uuid
from pathlib import Path

from app.core.config import settings

_TOKEN_RE = re.compile(r"\b\w+\b")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class BM25Index:
    def __init__(self, document_id: uuid.UUID) -> None:
        self.document_id = document_id
        self._path = Path(settings.VECTOR_STORE_PATH) / str(document_id) / "bm25.pkl"
        self._bm25 = None
        self._vector_ids: list[int] = []

    def build(self, texts: list[str], vector_ids: list[int]) -> None:
        from rank_bm25 import BM25Okapi

        if len(texts) != len(vector_ids):
            raise ValueError("texts and vector_ids must be the same length")

        tokenized_corpus = [_tokenize(t) for t in texts]
        self._bm25 = BM25Okapi(tokenized_corpus)
        self._vector_ids = vector_ids

    def search(self, query: str, top_k: int) -> list[tuple[int, float]]:
        """Returns [(vector_id, bm25_score), ...] sorted best-first."""
        if self._bm25 is None:
            self._load()
        if self._bm25 is None:
            return []

        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(self._vector_ids, scores), key=lambda pair: pair[1], reverse=True)
        return [(vid, float(score)) for vid, score in ranked[:top_k] if score > 0]

    def persist(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "wb") as f:
            pickle.dump({"bm25": self._bm25, "vector_ids": self._vector_ids}, f)

    def _load(self) -> None:
        if not self._path.exists():
            return
        with open(self._path, "rb") as f:
            data = pickle.load(f)
        self._bm25 = data["bm25"]
        self._vector_ids = data["vector_ids"]
