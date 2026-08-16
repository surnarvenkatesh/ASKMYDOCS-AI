"""
Document service — business logic for upload, listing, deletion,
renaming, and re-indexing. Coordinates the repository (DB), the
filesystem (raw file storage), and the ingestion pipeline (parsing /
chunking / embedding / indexing).
"""
from __future__ import annotations

import uuid
from pathlib import Path

from app.core.config import settings
from app.ingestion.parsers import ParsingError, document_type_from_filename
from app.ingestion.pipeline import IngestionError, run_ingestion_pipeline
from app.models.document import Document, DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.retrieval.bm25_index import BM25Index
from app.retrieval.embeddings import get_embedding_provider
from app.retrieval.vector_store import VectorStore


class DocumentServiceError(Exception):
    """Raised for user-facing document service failures (4xx-worthy)."""


class DocumentService:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self._documents = document_repository

    def _validate_upload(self, filename: str, file_size_bytes: int) -> None:
        try:
            doc_type = document_type_from_filename(filename)
        except ParsingError as exc:
            raise DocumentServiceError(str(exc)) from exc

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size_bytes > max_bytes:
            raise DocumentServiceError(
                f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB upload limit"
            )
        return doc_type

    async def upload(self, owner_id: uuid.UUID, filename: str, file_bytes: bytes) -> Document:
        doc_type = self._validate_upload(filename, len(file_bytes))

        document = await self._documents.create(
            owner_id=owner_id,
            filename=filename,
            file_type=doc_type,
            file_path="",  # set below once we know the document id
            file_size_bytes=len(file_bytes),
        )

        storage_path = Path(settings.UPLOAD_DIR) / str(owner_id) / f"{document.id}_{filename}"
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(file_bytes)
        document.file_path = str(storage_path)

        await self._index_document(document, file_bytes)
        return document

    async def _index_document(self, document: Document, file_bytes: bytes) -> None:
        await self._documents.update_status(document, DocumentStatus.PROCESSING)
        try:
            embedding_provider = get_embedding_provider()
            chunks = run_ingestion_pipeline(
                document_id=document.id,
                file_bytes=file_bytes,
                document_type=document.file_type,
                embedding_provider=embedding_provider,
            )
            await self._documents.replace_chunks(document.id, chunks)
            await self._documents.update_status(document, DocumentStatus.INDEXED)
        except IngestionError as exc:
            await self._documents.update_status(document, DocumentStatus.FAILED, error_message=str(exc))
            raise DocumentServiceError(str(exc)) from exc

    async def reindex(self, document: Document) -> Document:
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise DocumentServiceError("Original file is missing from storage; re-upload required")

        VectorStore(document.id, dimension=1).delete()  # dimension irrelevant for delete
        await self._documents.bump_version(document)
        await self._index_document(document, file_path.read_bytes())
        return document

    async def rename(self, document: Document, new_filename: str) -> Document:
        if not new_filename.strip():
            raise DocumentServiceError("Filename cannot be empty")
        return await self._documents.rename(document, new_filename.strip())

    async def delete(self, document: Document) -> None:
        VectorStore(document.id, dimension=1).delete()
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
        await self._documents.delete(document)

    async def list_documents(
        self, owner_id: uuid.UUID, search: str | None, limit: int, offset: int
    ) -> tuple[list[Document], int]:
        return await self._documents.list_for_owner(owner_id, search=search, limit=limit, offset=offset)
