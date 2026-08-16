"""
Document-facing Pydantic schemas.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus, DocumentType


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    file_type: DocumentType
    file_size_bytes: int
    status: DocumentStatus
    error_message: str | None
    version: int
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentRead]
    total: int


class DocumentRenameRequest(BaseModel):
    filename: str


class ChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chunk_index: int
    content: str
    page_number: int | None
    token_count: int
