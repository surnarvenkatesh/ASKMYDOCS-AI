"""use clock_timestamp() instead of now() for created_at/updated_at defaults

Revision ID: 0005_use_clock_timestamp
Revises: 0004_message_feedback
Create Date: 2026-08-10 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_use_clock_timestamp"
down_revision: Union[str, None] = "0004_message_feedback"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = ["users", "documents", "document_chunks", "conversations", "messages"]


def upgrade() -> None:
    for table in _TABLES:
        op.alter_column(table, "created_at", server_default=sa.text("clock_timestamp()"))
        op.alter_column(table, "updated_at", server_default=sa.text("clock_timestamp()"))


def downgrade() -> None:
    for table in _TABLES:
        op.alter_column(table, "created_at", server_default=sa.text("now()"))
        op.alter_column(table, "updated_at", server_default=sa.text("now()"))
