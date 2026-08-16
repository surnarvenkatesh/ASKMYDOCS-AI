"""
Prompt builder — turns retrieved chunks + conversation history into the
system/user prompt pair sent to the LLM, with explicit citation-format
and no-hallucination instructions so the answer can be programmatically
validated afterward (see app.retrieval.citation_validator).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ContextChunk:
    ref_id: int  # 1-based index shown to the LLM, e.g. [1], [2]
    document_filename: str
    page_number: int | None
    content: str


SYSTEM_PROMPT = """You are AskMyDocs AI, an assistant that answers questions using ONLY the \
provided document excerpts. Follow these rules strictly:

1. Answer using only information found in the numbered excerpts below. Never use outside \
knowledge, even if you are confident it is correct.
2. Every factual claim in your answer must be followed by a citation marker like [1] or [2] \
referencing the excerpt number it came from. Use multiple markers like [1][3] if a claim draws \
on several excerpts.
3. If the excerpts do not contain enough information to answer the question, say so explicitly \
instead of guessing. Do not fabricate information, page numbers, or citations.
4. Be concise and directly answer the question first, then add supporting detail.
5. Format your answer in Markdown."""


def build_context_block(chunks: list[ContextChunk]) -> str:
    parts = []
    for chunk in chunks:
        location = f", p.{chunk.page_number}" if chunk.page_number else ""
        parts.append(f"[{chunk.ref_id}] (Source: {chunk.document_filename}{location})\n{chunk.content}")
    return "\n\n---\n\n".join(parts)


def build_user_prompt(question: str, chunks: list[ContextChunk], history_summary: str = "") -> str:
    context_block = build_context_block(chunks)
    history_section = f"\n\nPrevious conversation summary:\n{history_summary}\n" if history_summary else ""
    return (
        f"{history_section}\n"
        f"Document excerpts:\n\n{context_block}\n\n"
        f"---\n\n"
        f"Question: {question}"
    )
