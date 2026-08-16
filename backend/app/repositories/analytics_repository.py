"""
Analytics repository — read-only aggregate queries over a user's
documents, chunks, and chat messages for the analytics dashboard.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import DocumentChunk
from app.models.conversation import Conversation, Message, MessageRole
from app.models.document import Document


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_documents(self, owner_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Document).where(Document.owner_id == owner_id)
        )
        return result.scalar_one()

    async def count_chunks(self, owner_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.owner_id == owner_id)
        )
        return result.scalar_one()

    async def get_assistant_messages(self, owner_id: uuid.UUID, since: datetime) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .join(Conversation, Conversation.id == Message.conversation_id)
            .where(
                Conversation.owner_id == owner_id,
                Message.role == MessageRole.ASSISTANT,
                Message.created_at >= since,
            )
        )
        return list(result.scalars().all())

    async def count_daily_queries(self, owner_id: uuid.UUID, days: int = 14) -> list[tuple[str, int]]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._session.execute(
            select(
                func.date_trunc('day', func.timezone('Asia/Kolkata', Message.created_at)).label('day'),
                func.count(),
            )
            .join(Conversation, Conversation.id == Message.conversation_id)
            .where(
                Conversation.owner_id == owner_id,
                Message.role == MessageRole.ASSISTANT,
                Message.created_at >= since,
            )
            .group_by("day")
            .order_by("day")
        )
        return [(row[0].date().isoformat(), row[1]) for row in result.all()]
