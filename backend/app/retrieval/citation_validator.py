"""
Citation validation — the LLM is instructed to cite retrieved chunks as
[1], [2], etc. This module parses those markers out of the generated
answer and cross-checks them against the chunks actually sent as
context, so a hallucinated reference number (or an answer with zero
citations despite making factual claims) can be flagged rather than
silently trusted.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.retrieval.prompt_builder import ContextChunk

_CITATION_RE = re.compile(r"\[(\d+)\]")


@dataclass
class ValidatedCitation:
    ref_id: int
    document_filename: str
    page_number: int | None
    chunk_id: str
    confidence_score: float
    snippet: str


@dataclass
class CitationValidationResult:
    citations: list[ValidatedCitation]
    has_unverifiable_claims: bool  # answer contains prose but cites nothing
    invalid_ref_ids: list[int]  # ref numbers cited that don't exist in context


def extract_cited_ref_ids(answer_text: str) -> list[int]:
    seen: list[int] = []
    for match in _CITATION_RE.finditer(answer_text):
        ref_id = int(match.group(1))
        if ref_id not in seen:
            seen.append(ref_id)
    return seen


def validate_citations(
    answer_text: str,
    context_chunks: list[ContextChunk],
    chunk_scores: dict[int, float],
    chunk_ids: dict[int, str],
) -> CitationValidationResult:
    """
    chunk_scores / chunk_ids: keyed by ref_id, giving the cross-encoder
    confidence score and DB chunk id for each context chunk, so the
    citation payload returned to the client is fully traceable.
    """
    by_ref_id = {c.ref_id: c for c in context_chunks}
    cited_ref_ids = extract_cited_ref_ids(answer_text)

    valid_citations: list[ValidatedCitation] = []
    invalid_ref_ids: list[int] = []

    for ref_id in cited_ref_ids:
        chunk = by_ref_id.get(ref_id)
        if chunk is None:
            invalid_ref_ids.append(ref_id)
            continue
        valid_citations.append(
            ValidatedCitation(
                ref_id=ref_id,
                document_filename=chunk.document_filename,
                page_number=chunk.page_number,
                chunk_id=chunk_ids.get(ref_id, ""),
                confidence_score=chunk_scores.get(ref_id, 0.0),
                snippet=chunk.content[:280],
            )
        )

    # A "substantial" answer (more than a short refusal/apology) with zero
    # citations is suspicious — likely drifted from the provided context.
    is_refusal_like = len(answer_text.strip()) < 120 and (
        "don't" in answer_text.lower() or "not enough" in answer_text.lower() or "cannot" in answer_text.lower()
    )
    has_unverifiable_claims = not cited_ref_ids and not is_refusal_like and len(answer_text.strip()) > 0

    return CitationValidationResult(
        citations=valid_citations,
        has_unverifiable_claims=has_unverifiable_claims,
        invalid_ref_ids=invalid_ref_ids,
    )
