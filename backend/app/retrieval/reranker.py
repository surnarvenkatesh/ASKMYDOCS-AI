"""
Cross-encoder re-ranking.

RRF gives a fast, decent first pass, but bi-encoder similarity and BM25
overlap both miss semantic relationships between the *specific* query
and each candidate chunk. A cross-encoder scores (query, chunk) pairs
jointly and is far more accurate, but too slow to run over the whole
corpus — so it only re-scores the top-N candidates that already survived
RRF fusion.
"""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings


@lru_cache
def _get_cross_encoder():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(settings.CROSS_ENCODER_MODEL)


def rerank(query: str, candidates: list[tuple[int, str]], top_k: int = settings.RERANK_TOP_K) -> list[tuple[int, str, float]]:
    """
    candidates: [(vector_id, chunk_text), ...]
    Returns the top_k candidates re-scored and sorted by cross-encoder
    relevance: [(vector_id, chunk_text, score), ...]
    """
    if not candidates:
        return []

    model = _get_cross_encoder()
    pairs = [(query, text) for _, text in candidates]
    scores = model.predict(pairs)

    scored = [
        (vector_id, text, float(score))
        for (vector_id, text), score in zip(candidates, scores)
    ]
    scored.sort(key=lambda item: item[2], reverse=True)
    return scored[:top_k]
