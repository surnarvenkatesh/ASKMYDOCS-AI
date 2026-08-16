"""
Chat-facing Pydantic schemas.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.conversation import MessageRole


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[uuid.UUID] | None = Field(
        default=None,
        description="Restrict retrieval to these documents. Omit to search all of the user's documents.",
    )


class CitationPayload(BaseModel):
    ref_id: int
    document_filename: str
    page_number: int | None
    chunk_id: str
    confidence_score: float
    snippet: str


class ConversationCreate(BaseModel):
    title: str | None = None


class ConversationRenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: MessageRole
    content: str
    citations: list[dict]
    generation_metadata: dict
    created_at: datetime


class ConversationDetailRead(ConversationRead):
    messages: list[MessageRead]
