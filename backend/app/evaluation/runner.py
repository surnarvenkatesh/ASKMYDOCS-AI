"""
Evaluation runner — drives the golden dataset through a supplied
retrieval+generation function and aggregates the metrics in
app.evaluation.metrics into a pass/fail report for CI.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.evaluation.dataset import EvalExample, EvalRunResult
from app.evaluation.metrics import (
    MetricResult,
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
    latency_score,
)

# Signature the caller must implement: given a question, return the
# generated answer, the ids of documents retrieval surfaced, the [n]
# citation ref ids found in the answer, the invalid ones among them,
# and how long the whole round-trip took.
RagCallable = Callable[[EvalExample], Awaitable[EvalRunResult]]


@dataclass
class AggregateMetric:
    name: str
    mean_score: float
    passed: bool


@dataclass
class EvaluationReport:
    per_example: list[dict]
    aggregates: list[AggregateMetric]
    passed: bool


# Minimum acceptable mean score per metric before CI fails the build.
_THRESHOLDS = {
    "faithfulness": 0.8,
    "context_recall": 0.7,
    "context_precision": 0.5,
    "answer_relevancy": 0.3,  # lexical overlap is a weak proxy — keep threshold conservative
    "latency": 0.5,
}


async def run_evaluation(
    dataset: list[EvalExample],
    rag_fn: RagCallable,
) -> EvaluationReport:
    per_example: list[dict] = []
    scores_by_metric: dict[str, list[float]] = {name: [] for name in _THRESHOLDS}

    for example in dataset:
        result = await rag_fn(example)

        metrics: list[MetricResult] = [
            faithfulness(result.citation_ref_ids, result.invalid_citation_ref_ids),
            context_recall(result.retrieved_document_ids, example.expected_document_ids),
            context_precision(result.retrieved_document_ids, example.expected_document_ids),
            answer_relevancy(result.generated_answer, example.ground_truth_answer),
            latency_score(result.latency_ms),
        ]

        for metric in metrics:
            scores_by_metric[metric.name].append(metric.score)

        per_example.append(
            {
                "question": example.question,
                "generated_answer": result.generated_answer,
                "metrics": {m.name: {"score": m.score, "details": m.details} for m in metrics},
            }
        )

    aggregates = []
    for name, scores in scores_by_metric.items():
        mean_score = sum(scores) / len(scores) if scores else 0.0
        aggregates.append(
            AggregateMetric(name=name, mean_score=round(mean_score, 4), passed=mean_score >= _THRESHOLDS[name])
        )

    overall_passed = all(a.passed for a in aggregates)

    return EvaluationReport(per_example=per_example, aggregates=aggregates, passed=overall_passed)
