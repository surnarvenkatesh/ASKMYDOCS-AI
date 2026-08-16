"""
Shared model mixins: UUID primary keys and created_at/updated_at timestamps.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    # Uses clock_timestamp() rather than now(): Postgres freezes now() to a
    # single value for the whole transaction, so two rows inserted in the
    # same uncommitted transaction (e.g. a user message and its assistant
    # reply, only committed together at the end of the request) would get
    # IDENTICAL created_at values with now() — breaking chronological
    # ordering. clock_timestamp() reflects actual wall-clock time and
    # advances between statements even within one transaction.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
        onupdate=func.clock_timestamp(),
        nullable=False,
    )
