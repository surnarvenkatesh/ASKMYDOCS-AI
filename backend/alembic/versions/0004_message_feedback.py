"""add feedback column to messages table

Revision ID: 0004_message_feedback
Revises: 0003_conversations
Create Date: 2026-08-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_message_feedback"
down_revision: Union[str, None] = "0003_conversations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("feedback", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "feedback")
