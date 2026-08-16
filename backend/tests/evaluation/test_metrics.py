"""
Tests for app.evaluation.metrics — these are the metrics computed on
every PR by the CI evaluation gate (see .github/workflows/ci.yml).
"""
import pytest

from app.evaluation.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
    latency_score,
)


@pytest.mark.evaluation
class TestFaithfulness:
    def test_all_citations_valid_scores_one(self):
        result = faithfulness(citation_ref_ids=[1, 2, 3], invalid_citation_ref_ids=[])
        assert result.score == 1.0

    def test_half_invalid_citations_scores_half(self):
        result = faithfulness(citation_ref_ids=[1, 2], invalid_citation_ref_ids=[2])
        assert result.score == 0.5

    def test_no_citations_scores_zero(self):
        result = faithfulness(citation_ref_ids=[], invalid_citation_ref_ids=[])
        assert result.score == 0.0


@pytest.mark.evaluation
class TestContextRecall:
    def test_full_recall(self):
        result = context_recall(["doc-a", "doc-b"], ["doc-a"])
        assert result.score == 1.0

    def test_partial_recall(self):
        result = context_recall(["doc-a"], ["doc-a", "doc-b"])
        assert result.score == 0.5

    def test_no_expected_documents_scores_one(self):
        result = context_recall(["doc-a"], [])
        assert result.score == 1.0


@pytest.mark.evaluation
class TestContextPrecision:
    def test_all_retrieved_relevant(self):
        result = context_precision(["doc-a", "doc-b"], ["doc-a", "doc-b"])
        assert result.score == 1.0

    def test_half_relevant(self):
        result = context_precision(["doc-a", "doc-c"], ["doc-a"])
        assert result.score == 0.5

    def test_nothing_retrieved_scores_zero(self):
        result = context_precision([], ["doc-a"])
        assert result.score == 0.0


@pytest.mark.evaluation
class TestAnswerRelevancy:
    def test_identical_answers_score_high(self):
        result = answer_relevancy("Revenue grew by 20 percent", "Revenue grew by 20 percent")
        assert result.score == 1.0

    def test_unrelated_answers_score_low(self):
        result = answer_relevancy("The weather is sunny today", "Revenue grew by 20 percent")
        assert result.score < 0.3

    def test_empty_answer_scores_zero(self):
        result = answer_relevancy("", "Revenue grew by 20 percent")
        assert result.score == 0.0


@pytest.mark.evaluation
class TestLatencyScore:
    def test_under_target_scores_one(self):
        assert latency_score(1000, target_ms=3000).score == 1.0

    def test_at_target_scores_one(self):
        assert latency_score(3000, target_ms=3000).score == 1.0

    def test_over_target_decays(self):
        result = latency_score(6000, target_ms=3000)
        assert 0.0 < result.score < 1.0

    def test_far_over_target_scores_near_zero(self):
        result = latency_score(9000, target_ms=3000)
        assert result.score == 0.0
