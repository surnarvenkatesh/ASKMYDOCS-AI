"""
Reciprocal Rank Fusion (RRF).

Combines two independently-ranked result lists (BM25 keyword search and
vector similarity search) into a single fused ranking, without needing
to normalize or compare their differently-scaled scores directly. Each
item's fused score is the sum of 1/(k + rank) across every list it
appears in — items ranked highly in *either* list bubble to the top,
and items appearing in *both* get compounded credit.
"""
from __future__ import annotations

from typing import Hashable, TypeVar

K = TypeVar("K", bound=Hashable)


def reciprocal_rank_fusion(
    ranked_lists: list[list[K]],
    k: int = 60,
) -> list[tuple[K, float]]:
    """
    ranked_lists: one list per retrieval method, each a list of item keys
    ordered best-first. Keys just need to be hashable (int vector_ids,
    or (document_id, vector_id) tuples when fusing across documents).
    Returns [(key, fused_score), ...] sorted best-first.
    """
    scores: dict[K, float] = {}
    for ranked_list in ranked_lists:
        for rank, key in enumerate(ranked_list, start=1):
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)

    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
