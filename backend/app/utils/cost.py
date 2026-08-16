"""
Token usage estimation and cost calculation.

Uses a cheap ~4-chars-per-token heuristic rather than a real tokenizer,
which is accurate enough for cost *estimates* shown on the analytics
dashboard without adding a tiktoken dependency to the hot path.
"""
from __future__ import annotations

from app.core.config import settings

# USD per 1K tokens, (prompt, completion). Update as pricing changes.
_PRICING_PER_1K_TOKENS: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4o": (0.0025, 0.01),
    "llama3.1": (0.0, 0.0),  # local Ollama — no per-token cost
}


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def estimate_cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    model = settings.OPENAI_MODEL if settings.LLM_PROVIDER == "openai" else settings.OLLAMA_MODEL
    prompt_price, completion_price = _PRICING_PER_1K_TOKENS.get(model, (0.0, 0.0))
    return round((prompt_tokens / 1000) * prompt_price + (completion_tokens / 1000) * completion_price, 6)
