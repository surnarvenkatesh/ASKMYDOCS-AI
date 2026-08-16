"""
Evaluation metrics.

These are deliberately lightweight, deterministic re-implementations of
the metric *concepts* RAGAS and DeepEval provide (faithfulness, context
recall/precision, answer relevancy), so the CI evaluation gate can run
on every PR without needing a live LLM judge or network access. For a
deeper, LLM-graded evaluation in a real deployment, see
`app/evaluation/ragas_runner.py`, which wires the same EvalExample
dataset into the real `ragas`/`deepeval` libraries (both already in
requirements.txt) when an LLM judge is configured.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_WORD_RE = re.compile(r"\b\w+\b")

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "in", "on", "of", "to",
    "and", "or", "for", "with", "what", "how", "did", "does", "do",
}


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text) if w.lower() not in _STOPWORDS}


@dataclass
class MetricResult:
    name: str
    score: float  # 0.0 - 1.0, higher is better
    details: str = ""


def faithfulness(citation_ref_ids: list[int], invalid_citation_ref_ids: list[int]) -> MetricResult:
    """
    Fraction of cited claims that trace back to a real retrieved chunk.
    An answer that cites nothing at all scores 0 (nothing to verify);
    an answer whose citations are all valid scores 1.
    """
    total_refs = len(citation_ref_ids)
    if total_refs == 0:
        return MetricResult("faithfulness", 0.0, "No citations to verify")

    valid = total_refs - len(invalid_citation_ref_ids)
    score = valid / total_refs
    return MetricResult("faithfulness", score, f"{valid}/{total_refs} citations verified")


def context_recall(retrieved_document_ids: list[str], expected_document_ids: list[str]) -> MetricResult:
    """Did retrieval surface at least the documents known to be relevant?"""
    if not expected_document_ids:
        return MetricResult("context_recall", 1.0, "No expected documents specified")

    retrieved = set(retrieved_document_ids)
    expected = set(expected_document_ids)
    hit = len(retrieved & expected)
    score = hit / len(expected)
    return MetricResult("context_recall", score, f"{hit}/{len(expected)} expected documents retrieved")


def context_precision(retrieved_document_ids: list[str], expected_document_ids: list[str]) -> MetricResult:
    """Of what was retrieved, how much was actually relevant?"""
    if not retrieved_document_ids:
        return MetricResult("context_precision", 0.0, "Nothing retrieved")

    retrieved = set(retrieved_document_ids)
    expected = set(expected_document_ids)
    relevant = len(retrieved & expected)
    score = relevant / len(retrieved)
    return MetricResult("context_precision", score, f"{relevant}/{len(retrieved)} retrieved docs relevant")


def answer_relevancy(generated_answer: str, ground_truth_answer: str) -> MetricResult:
    """
    Lexical Jaccard overlap between the generated and ground-truth
    answer, as a network-free proxy for semantic answer relevancy.
    Swap in an embedding-cosine version (see EmbeddingProvider) for a
    stronger signal when a model is available.
    """
    generated_tokens = _tokenize(generated_answer)
    truth_tokens = _tokenize(ground_truth_answer)

    if not generated_tokens or not truth_tokens:
        return MetricResult("answer_relevancy", 0.0, "Empty answer or ground truth")

    intersection = generated_tokens & truth_tokens
    union = generated_tokens | truth_tokens
    score = len(intersection) / len(union)
    return MetricResult("answer_relevancy", score, f"Jaccard overlap {len(intersection)}/{len(union)}")


def latency_score(latency_ms: float, target_ms: float = 3000.0) -> MetricResult:
    """1.0 at or under target latency, decaying linearly to 0 at 3x target."""
    if latency_ms <= target_ms:
        return MetricResult("latency", 1.0, f"{latency_ms:.0f}ms <= target {target_ms:.0f}ms")
    ceiling = target_ms * 3
    score = max(0.0, 1 - (latency_ms - target_ms) / (ceiling - target_ms))
    return MetricResult("latency", round(score, 4), f"{latency_ms:.0f}ms vs target {target_ms:.0f}ms")
