"""
Unit tests for app.retrieval.citation_validator.
"""
import pytest

from app.retrieval.citation_validator import extract_cited_ref_ids, validate_citations
from app.retrieval.prompt_builder import ContextChunk


def _chunks():
    return [
        ContextChunk(ref_id=1, document_filename="a.pdf", page_number=2, content="Revenue grew 20%."),
        ContextChunk(ref_id=2, document_filename="b.docx", page_number=None, content="Costs fell 5%."),
    ]


@pytest.mark.unit
class TestExtractCitedRefIds:
    def test_extracts_unique_ordered_ids(self):
        assert extract_cited_ref_ids("Revenue grew [1] and costs fell [2][1].") == [1, 2]

    def test_no_citations_returns_empty(self):
        assert extract_cited_ref_ids("No citations here.") == []


@pytest.mark.unit
class TestValidateCitations:
    def test_valid_citation_is_kept(self):
        result = validate_citations(
            "Revenue grew 20% [1].",
            _chunks(),
            chunk_scores={1: 0.9, 2: 0.8},
            chunk_ids={1: "chunk-1", 2: "chunk-2"},
        )
        assert len(result.citations) == 1
        assert result.citations[0].document_filename == "a.pdf"
        assert result.citations[0].page_number == 2
        assert result.invalid_ref_ids == []

    def test_hallucinated_ref_id_flagged_invalid(self):
        result = validate_citations(
            "According to the data [5].",
            _chunks(),
            chunk_scores={1: 0.9, 2: 0.8},
            chunk_ids={1: "chunk-1", 2: "chunk-2"},
        )
        assert result.invalid_ref_ids == [5]
        assert result.citations == []

    def test_uncited_substantial_answer_flagged_unverifiable(self):
        result = validate_citations(
            "Revenue definitely grew by a huge amount this quarter across every region.",
            _chunks(),
            chunk_scores={},
            chunk_ids={},
        )
        assert result.has_unverifiable_claims is True

    def test_refusal_style_answer_not_flagged(self):
        result = validate_citations(
            "I don't have enough information to answer that.",
            _chunks(),
            chunk_scores={},
            chunk_ids={},
        )
        assert result.has_unverifiable_claims is False
