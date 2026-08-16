"""
Evaluation dataset — golden examples used by the RAG evaluation suite.

Each example pairs a question with the document(s) that should be
retrieved to answer it and a ground-truth answer, so retrieval quality
(precision/recall) and generation quality (faithfulness/relevancy) can
both be scored without a human in the loop.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvalExample:
    question: str
    ground_truth_answer: str
    expected_document_ids: list[str] = field(default_factory=list)


@dataclass
class EvalRunResult:
    example: EvalExample
    generated_answer: str
    retrieved_document_ids: list[str]
    citation_ref_ids: list[int]
    invalid_citation_ref_ids: list[int]
    latency_ms: float


def load_sample_dataset() -> list[EvalExample]:
    """
    A small built-in dataset so the evaluation suite has something to run
    against out of the box. Real deployments should replace this with
    domain-specific golden examples (see docs/EVALUATION.md).
    """
    return [
        EvalExample(
            question="What was the change in operating margin last quarter?",
            ground_truth_answer="Operating margin improved, driven by a 12% reduction in cloud infrastructure spend.",
            expected_document_ids=["q3-board-deck"],
        ),
        EvalExample(
            question="What is the termination notice period in the vendor contract?",
            ground_truth_answer="The contract requires 60 days' written notice prior to termination.",
            expected_document_ids=["vendor-contract"],
        ),
        EvalExample(
            question="Summarize the main risk factors mentioned in the annual report.",
            ground_truth_answer="Key risks include supply chain concentration, currency exposure, and regulatory change.",
            expected_document_ids=["annual-report"],
        ),
    ]
