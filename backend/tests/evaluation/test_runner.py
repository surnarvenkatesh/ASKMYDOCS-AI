"""
Tests for app.evaluation.runner.run_evaluation.
"""
import pytest

from app.evaluation.dataset import EvalExample, EvalRunResult
from app.evaluation.runner import run_evaluation


@pytest.mark.evaluation
class TestRunEvaluation:
    async def test_perfect_run_passes_all_thresholds(self):
        dataset = [
            EvalExample(
                question="What changed?",
                ground_truth_answer="Revenue grew by 20 percent",
                expected_document_ids=["doc-a"],
            )
        ]

        async def perfect_rag(example: EvalExample) -> EvalRunResult:
            return EvalRunResult(
                example=example,
                generated_answer="Revenue grew by 20 percent",
                retrieved_document_ids=["doc-a"],
                citation_ref_ids=[1],
                invalid_citation_ref_ids=[],
                latency_ms=500,
            )

        report = await run_evaluation(dataset, perfect_rag)
        assert report.passed is True
        assert all(a.passed for a in report.aggregates)

    async def test_poor_run_fails_thresholds(self):
        dataset = [
            EvalExample(
                question="What changed?",
                ground_truth_answer="Revenue grew by 20 percent",
                expected_document_ids=["doc-a"],
            )
        ]

        async def poor_rag(example: EvalExample) -> EvalRunResult:
            return EvalRunResult(
                example=example,
                generated_answer="I have no idea about anything unrelated",
                retrieved_document_ids=["doc-z"],
                citation_ref_ids=[1, 2],
                invalid_citation_ref_ids=[1, 2],
                latency_ms=15000,
            )

        report = await run_evaluation(dataset, poor_rag)
        assert report.passed is False
        failed_metrics = {a.name for a in report.aggregates if not a.passed}
        assert "faithfulness" in failed_metrics
        assert "context_recall" in failed_metrics

    async def test_per_example_detail_is_recorded(self):
        dataset = [EvalExample(question="Q1", ground_truth_answer="A1", expected_document_ids=[])]

        async def rag_fn(example: EvalExample) -> EvalRunResult:
            return EvalRunResult(
                example=example,
                generated_answer="A1",
                retrieved_document_ids=[],
                citation_ref_ids=[],
                invalid_citation_ref_ids=[],
                latency_ms=100,
            )

        report = await run_evaluation(dataset, rag_fn)
        assert len(report.per_example) == 1
        assert report.per_example[0]["question"] == "Q1"
        assert "faithfulness" in report.per_example[0]["metrics"]
