"""
Unit tests for app.utils.cost.
"""
import pytest

from app.utils.cost import estimate_cost_usd, estimate_tokens


@pytest.mark.unit
class TestEstimateTokens:
    def test_empty_string_returns_at_least_one(self):
        assert estimate_tokens("") == 1

    def test_scales_roughly_with_length(self):
        short = estimate_tokens("hello")
        long = estimate_tokens("hello " * 100)
        assert long > short


@pytest.mark.unit
class TestEstimateCost:
    def test_zero_tokens_costs_zero_for_local_model(self, monkeypatch):
        from app.core.config import settings

        monkeypatch.setattr(settings, "LLM_PROVIDER", "ollama")
        monkeypatch.setattr(settings, "OLLAMA_MODEL", "llama3.1")
        assert estimate_cost_usd(1000, 1000) == 0.0

    def test_unknown_model_defaults_to_zero_cost(self, monkeypatch):
        from app.core.config import settings

        monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
        monkeypatch.setattr(settings, "OPENAI_MODEL", "some-future-model")
        assert estimate_cost_usd(1000, 1000) == 0.0

    def test_known_model_computes_nonzero_cost(self, monkeypatch):
        from app.core.config import settings

        monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
        monkeypatch.setattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
        cost = estimate_cost_usd(1000, 1000)
        assert cost > 0
