"""
Optional real RAGAS/DeepEval integration.

`app.evaluation.runner` uses fast, network-free metric approximations so
the CI evaluation gate can run on every PR without a live LLM judge.
This module wires the same EvalExample dataset into the real `ragas`
and `deepeval` libraries for a deeper, LLM-graded evaluation — useful
as a periodic (e.g. nightly) job once you have an LLM judge configured,
but NOT part of the default CI gate since it costs real API calls and
requires network access.

Usage (outside CI, with OPENAI_API_KEY set):

    from app.evaluation.ragas_runner import run_ragas_evaluation
    report = await run_ragas_evaluation(dataset, rag_fn)
"""
from __future__ import annotations

from app.core.config import settings
from app.evaluation.dataset import EvalExample
from app.evaluation.runner import RagCallable


async def run_ragas_evaluation(dataset: list[EvalExample], rag_fn: RagCallable) -> dict:
    if not settings.RAGAS_ENABLED:
        raise RuntimeError("RAGAS_ENABLED is false — enable it in .env to run this evaluation")
    if settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY must be set to use RAGAS/DeepEval as an LLM judge")

    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

    rows = []
    for example in dataset:
        result = await rag_fn(example)
        rows.append(
            {
                "question": example.question,
                "answer": result.generated_answer,
                "contexts": result.retrieved_document_ids,
                "ground_truth": example.ground_truth_answer,
            }
        )

    hf_dataset = Dataset.from_list(rows)
    result = evaluate(
        hf_dataset,
        metrics=[faithfulness, context_recall, context_precision, answer_relevancy],
    )
    return result.to_pandas().to_dict(orient="records")
