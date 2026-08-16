"""
Document repository — all direct DB access for documents and their chunks.
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ingestion.pipeline import IngestedChunk
from app.models.chunk import DocumentChunk
from app.models.document import Document, DocumentStatus, DocumentType


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        owner_id: uuid.UUID,
        filename: str,
        file_type: DocumentType,
        file_path: str,
        file_size_bytes: int,
    ) -> Document:
        document = Document(
            owner_id=owner_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            status=DocumentStatus.PENDING,
        )
        self._session.add(document)
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def get_by_id(self, document_id: uuid.UUID, owner_id: uuid.UUID) -> Document | None:
        result = await self._session.execute(
            select(Document).where(Document.id == document_id, Document.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def get_with_chunks(self, document_id: uuid.UUID, owner_id: uuid.UUID) -> Document | None:
        result = await self._session.execute(
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.id == document_id, Document.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def list_for_owner(
        self, owner_id: uuid.UUID, search: str | None = None, limit: int = 50, offset: int = 0
    ) -> tuple[list[Document], int]:
        query = select(Document).where(Document.owner_id == owner_id)
        count_query = select(func.count()).select_from(Document).where(Document.owner_id == owner_id)

        if search:
            pattern = f"%{search}%"
            query = query.where(Document.filename.ilike(pattern))
            count_query = count_query.where(Document.filename.ilike(pattern))

        query = query.order_by(Document.created_at.desc()).limit(limit).offset(offset)

        result = await self._session.execute(query)
        total = (await self._session.execute(count_query)).scalar_one()
        return list(result.scalars().all()), total

    async def update_status(
        self, document: Document, status: DocumentStatus, error_message: str | None = None
    ) -> Document:
        document.status = status
        document.error_message = error_message
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def rename(self, document: Document, filename: str) -> Document:
        document.filename = filename
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def bump_version(self, document: Document) -> Document:
        document.version += 1
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def delete(self, document: Document) -> None:
        await self._session.delete(document)
        await self._session.flush()

    async def replace_chunks(self, document_id: uuid.UUID, chunks: list[IngestedChunk]) -> None:
        await self._session.execute(
            DocumentChunk.__table__.delete().where(DocumentChunk.document_id == document_id)
        )
        for chunk in chunks:
            self._session.add(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    token_count=chunk.token_count,
                    vector_id=chunk.vector_id,
                    chunk_metadata=chunk.metadata,
                )
            )
        await self._session.flush()
