"""
Document management endpoints — upload, list, search, rename, delete,
re-index, download. All scoped to the authenticated user's own documents.
"""
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_document_repository, get_document_service
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import (
    ChunkRead,
    DocumentListResponse,
    DocumentRead,
    DocumentRenameRequest,
)
from app.services.document_service import DocumentService, DocumentServiceError

router = APIRouter(prefix="/documents", tags=["Documents"])


async def _get_owned_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    document_repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> Document:
    document = await document_repository.get_by_id(document_id, owner_id=current_user.id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document (PDF, DOCX, TXT, or Markdown) for indexing",
)
async def upload_document(
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Document:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing filename")

    file_bytes = await file.read()
    try:
        document = await document_service.upload(current_user.id, file.filename, file_bytes)
    except DocumentServiceError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    await db.commit()
    return document


@router.get("", response_model=DocumentListResponse, summary="List my documents")
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    search: str | None = Query(default=None, description="Filter by filename substring"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> DocumentListResponse:
    documents, total = await document_service.list_documents(current_user.id, search, limit, offset)
    return DocumentListResponse(documents=documents, total=total)


@router.get("/{document_id}", response_model=DocumentRead, summary="Get document metadata")
async def get_document(document: Annotated[Document, Depends(_get_owned_document)]) -> Document:
    return document


@router.get(
    "/{document_id}/chunks",
    response_model=list[ChunkRead],
    summary="View the indexed chunks for a document",
)
async def get_document_chunks(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    document_repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> list:
    document = await document_repository.get_with_chunks(document_id, owner_id=current_user.id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document.chunks


@router.get("/{document_id}/download", summary="Download the original file")
async def download_document(document: Annotated[Document, Depends(_get_owned_document)]) -> FileResponse:
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing from storage")
    return FileResponse(path=file_path, filename=document.filename)


@router.patch("/{document_id}", response_model=DocumentRead, summary="Rename a document")
async def rename_document(
    body: DocumentRenameRequest,
    document: Annotated[Document, Depends(_get_owned_document)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Document:
    try:
        updated = await document_service.rename(document, body.filename)
    except DocumentServiceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    await db.commit()
    return updated


@router.post("/{document_id}/reindex", response_model=DocumentRead, summary="Re-run ingestion for a document")
async def reindex_document(
    document: Annotated[Document, Depends(_get_owned_document)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Document:
    try:
        updated = await document_service.reindex(document)
    except DocumentServiceError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    await db.commit()
    return updated


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document")
async def delete_document(
    document: Annotated[Document, Depends(_get_owned_document)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await document_service.delete(document)
    await db.commit()
