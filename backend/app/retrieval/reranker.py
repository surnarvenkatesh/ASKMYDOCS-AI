"""
Reranking via Cohere's hosted rerank REST API.
RRF gives a fast, decent first pass, but bi-encoder similarity and BM25
overlap both miss semantic relationships between the *specific* query
and each candidate chunk. A dedicated reranker scores (query, chunk)
pairs jointly and is far more accurate, but too slow/heavy to run
locally on a memory-constrained deployment — so this calls Cohere's
REST API directly (avoiding their SDK, which pins an old numpy that
conflicts with scipy/faiss) rather than loading a local model.
"""
from __future__ import annotations

import httpx

from app.core.config import settings

_COHERE_RERANK_URL = "https://api.cohere.com/v2/rerank"


def rerank(query: str, candidates: list[tuple[int, str]], top_k: int | None = None) -> list[tuple[int, str, float]]:
    """
    candidates: [(vector_id, chunk_text), ...]
    Returns the top_k candidates re-scored and sorted by reranker
    relevance: [(vector_id, chunk_text, score), ...]
    """
    if not candidates:
        return []

    top_k = top_k or settings.RERANK_TOP_K

    if not settings.COHERE_API_KEY:
        return [(vid, text, 0.0) for vid, text in candidates[:top_k]]

    documents = [text for _, text in candidates]
    try:
        response = httpx.post(
            _COHERE_RERANK_URL,
            headers={
                "Authorization": f"Bearer {settings.COHERE_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "rerank-v3.5",
                "query": query,
                "documents": documents,
                "top_n": min(top_k, len(documents)),
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, httpx.TimeoutException):
        return [(vid, text, 0.0) for vid, text in candidates[:top_k]]

    scored: list[tuple[int, str, float]] = []
    for result in data["results"]:
        vector_id, text = candidates[result["index"]]
        scored.append((vector_id, text, float(result["relevance_score"])))
    return scored
