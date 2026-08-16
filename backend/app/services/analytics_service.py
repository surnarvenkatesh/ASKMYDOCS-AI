"""
Analytics service — turns raw repository aggregates plus per-message
generation metadata (recorded by ChatService) into the dashboard summary.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository) -> None:
        self._repo = analytics_repository

    async def get_summary(self, owner_id: uuid.UUID, days: int = 14) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        documents_count = await self._repo.count_documents(owner_id)
        chunks_count = await self._repo.count_chunks(owner_id)
        assistant_messages = await self._repo.get_assistant_messages(owner_id, since)
        daily_counts = dict(await self._repo.count_daily_queries(owner_id, days=days))

        today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
        daily_queries = [
            {
                "date": (day := today - timedelta(days=offset)).isoformat(),
                "count": daily_counts.get(day.isoformat(), 0),
            }
            for offset in range(days - 1, -1, -1)
        ]

        response_times = [
            m.generation_metadata.get("generation_ms", 0)
            for m in assistant_messages
            if m.generation_metadata.get("generation_ms") is not None
        ]
        retrieval_times = [
            m.generation_metadata.get("retrieval_ms", 0)
            for m in assistant_messages
            if m.generation_metadata.get("retrieval_ms") is not None
        ]

        prompt_tokens = sum(
            m.generation_metadata.get("token_usage", {}).get("prompt_tokens", 0) for m in assistant_messages
        )
        completion_tokens = sum(
            m.generation_metadata.get("token_usage", {}).get("completion_tokens", 0) for m in assistant_messages
        )
        total_cost = sum(m.generation_metadata.get("estimated_cost_usd", 0.0) for m in assistant_messages)

        # "Retrieval accuracy" here means the share of answers whose
        # citations were fully verifiable (no fabricated ref ids, at
        # least one citation for substantial answers) — a live proxy
        # for the RAGAS faithfulness metric computed offline in the
        # evaluation pipeline (see app/evaluation).
        verifiable = [
            m for m in assistant_messages if not m.generation_metadata.get("invalid_citation_refs")
        ]
        retrieval_accuracy = (len(verifiable) / len(assistant_messages)) if assistant_messages else None

        return {
            "documents_count": documents_count,
            "embeddings_count": chunks_count,
            "total_queries": len(assistant_messages),
            "avg_response_time_ms": round(sum(response_times) / len(response_times), 1)
            if response_times
            else None,
            "avg_retrieval_time_ms": round(sum(retrieval_times) / len(retrieval_times), 1)
            if retrieval_times
            else None,
            "retrieval_accuracy": round(retrieval_accuracy, 4) if retrieval_accuracy is not None else None,
            "token_usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
            "estimated_cost_usd": round(total_cost, 4),
            "daily_queries": daily_queries,
        }
