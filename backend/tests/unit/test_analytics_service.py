"""
Unit tests for app.services.analytics_service.AnalyticsService.
"""
import uuid
from dataclasses import dataclass, field

import pytest

from app.services.analytics_service import AnalyticsService


@dataclass
class FakeMessage:
    generation_metadata: dict = field(default_factory=dict)


class FakeAnalyticsRepository:
    def __init__(self, documents=0, chunks=0, messages=None, daily=None):
        self._documents = documents
        self._chunks = chunks
        self._messages = messages or []
        self._daily = daily or []

    async def count_documents(self, owner_id):
        return self._documents

    async def count_chunks(self, owner_id):
        return self._chunks

    async def get_assistant_messages(self, owner_id, since):
        return self._messages

    async def count_daily_queries(self, owner_id, days=14):
        return self._daily


@pytest.mark.unit
class TestAnalyticsService:
    async def test_summary_with_no_activity(self):
        repo = FakeAnalyticsRepository(documents=3, chunks=42)
        service = AnalyticsService(repo)
        summary = await service.get_summary(uuid.uuid4())

        assert summary["documents_count"] == 3
        assert summary["embeddings_count"] == 42
        assert summary["total_queries"] == 0
        assert summary["avg_response_time_ms"] is None
        assert summary["retrieval_accuracy"] is None
        assert summary["daily_queries"] == []

    async def test_summary_averages_response_times(self):
        messages = [
            FakeMessage({"generation_ms": 200, "retrieval_ms": 50, "invalid_citation_refs": []}),
            FakeMessage({"generation_ms": 400, "retrieval_ms": 100, "invalid_citation_refs": []}),
        ]
        repo = FakeAnalyticsRepository(messages=messages)
        service = AnalyticsService(repo)
        summary = await service.get_summary(uuid.uuid4())

        assert summary["avg_response_time_ms"] == 300.0
        assert summary["avg_retrieval_time_ms"] == 75.0
        assert summary["total_queries"] == 2

    async def test_retrieval_accuracy_reflects_invalid_citations(self):
        messages = [
            FakeMessage({"invalid_citation_refs": []}),
            FakeMessage({"invalid_citation_refs": [5]}),
        ]
        repo = FakeAnalyticsRepository(messages=messages)
        service = AnalyticsService(repo)
        summary = await service.get_summary(uuid.uuid4())

        assert summary["retrieval_accuracy"] == 0.5

    async def test_token_usage_and_cost_are_summed(self):
        messages = [
            FakeMessage({"token_usage": {"prompt_tokens": 100, "completion_tokens": 50}, "estimated_cost_usd": 0.001}),
            FakeMessage({"token_usage": {"prompt_tokens": 200, "completion_tokens": 75}, "estimated_cost_usd": 0.002}),
        ]
        repo = FakeAnalyticsRepository(messages=messages)
        service = AnalyticsService(repo)
        summary = await service.get_summary(uuid.uuid4())

        assert summary["token_usage"]["prompt_tokens"] == 300
        assert summary["token_usage"]["completion_tokens"] == 125
        assert summary["estimated_cost_usd"] == pytest.approx(0.003)

    async def test_daily_queries_pass_through(self):
        repo = FakeAnalyticsRepository(daily=[("2026-07-01", 5), ("2026-07-02", 3)])
        service = AnalyticsService(repo)
        summary = await service.get_summary(uuid.uuid4())

        assert summary["daily_queries"] == [
            {"date": "2026-07-01", "count": 5},
            {"date": "2026-07-02", "count": 3},
        ]
