"""
FAISS vector store wrapper.

One FAISS index per document, persisted under
`{VECTOR_STORE_PATH}/{document_id}/index.faiss`. Keeping indexes
per-document (rather than one giant global index) makes deletion,
re-indexing, and per-user isolation trivial — we never have to filter
a shared index by owner at query time.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import numpy as np

from app.core.config import settings


class VectorStore:
    def __init__(self, document_id: uuid.UUID, dimension: int) -> None:
        self.document_id = document_id
        self.dimension = dimension
        self._dir = Path(settings.VECTOR_STORE_PATH) / str(document_id)
        self._index_path = self._dir / "index.faiss"
        self._meta_path = self._dir / "meta.json"
        self._index = None

    def _ensure_index(self):
        import faiss

        if self._index is None:
            if self._index_path.exists():
                self._index = faiss.read_index(str(self._index_path))
            else:
                # Inner product on normalized vectors == cosine similarity.
                self._index = faiss.IndexFlatIP(self.dimension)
        return self._index

    def add(self, vectors: list[list[float]]) -> list[int]:
        """Add vectors, returning the assigned vector_id for each (its
        position in the index, stable for the lifetime of this store)."""
        index = self._ensure_index()
        start_id = index.ntotal
        matrix = np.array(vectors, dtype="float32")
        index.add(matrix)
        return list(range(start_id, start_id + len(vectors)))

    def search(self, query_vector: list[float], top_k: int) -> list[tuple[int, float]]:
        """Returns [(vector_id, similarity_score), ...] sorted best-first."""
        index = self._ensure_index()
        if index.ntotal == 0:
            return []
        query = np.array([query_vector], dtype="float32")
        scores, ids = index.search(query, min(top_k, index.ntotal))
        return [
            (int(vid), float(score))
            for vid, score in zip(ids[0], scores[0])
            if vid != -1
        ]

    def persist(self) -> None:
        import faiss

        self._dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._ensure_index(), str(self._index_path))
        self._meta_path.write_text(json.dumps({"dimension": self.dimension}))

    def delete(self) -> None:
        import shutil

        if self._dir.exists():
            shutil.rmtree(self._dir)
        self._index = None
