"""
Unit tests for app.retrieval.fusion.reciprocal_rank_fusion.
"""
import pytest

from app.retrieval.fusion import reciprocal_rank_fusion


@pytest.mark.unit
class TestReciprocalRankFusion:
    def test_single_list_preserves_order(self):
        result = reciprocal_rank_fusion([[10, 20, 30]], k=60)
        ids = [vid for vid, _ in result]
        assert ids == [10, 20, 30]

    def test_item_in_both_lists_ranks_above_item_in_one(self):
        bm25 = [1, 2, 3]
        vector = [2, 4, 5]
        result = reciprocal_rank_fusion([bm25, vector], k=60)
        ids = [vid for vid, _ in result]
        # id 2 appears in both lists -> should be ranked first
        assert ids[0] == 2

    def test_empty_lists_return_empty(self):
        assert reciprocal_rank_fusion([[], []]) == []

    def test_scores_are_descending(self):
        result = reciprocal_rank_fusion([[1, 2, 3], [3, 1, 2]], k=60)
        scores = [score for _, score in result]
        assert scores == sorted(scores, reverse=True)
