"""
API tests for /api/v1/documents/* — exercise route wiring and status
codes via FastAPI's TestClient, with the document service faked out so
no real DB, filesystem, or ML model is required.
"""
import io
import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.deps import (
    get_auth_service,
    get_current_user,
    get_document_repository,
    get_document_service,
    get_user_repository,
)
from app.core.config import settings
from app.main import app
from app.models.document import Document, DocumentStatus, DocumentType
from app.services.auth_service import AuthService
from app.services.document_service import DocumentService, DocumentServiceError
from tests.unit.test_auth_service import FakeUserRepository

PREFIX = f"{settings.API_V1_PREFIX}/documents"


class FakeDocumentRepository:
    def __init__(self):
        self.documents: dict[uuid.UUID, Document] = {}

    async def create(self, owner_id, filename, file_type, file_path, file_size_bytes):
        doc = Document(
            id=uuid.uuid4(),
            owner_id=owner_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path or "/tmp/fake",
            file_size_bytes=file_size_bytes,
            status=DocumentStatus.PENDING,
            version=1,
        )
        self.documents[doc.id] = doc
        return doc

    async def get_by_id(self, document_id, owner_id):
        doc = self.documents.get(document_id)
        return doc if doc and doc.owner_id == owner_id else None

    async def get_with_chunks(self, document_id, owner_id):
        doc = await self.get_by_id(document_id, owner_id)
        if doc is not None:
            doc.chunks = []
        return doc

    async def list_for_owner(self, owner_id, search=None, limit=50, offset=0):
        docs = [d for d in self.documents.values() if d.owner_id == owner_id]
        return docs, len(docs)

    async def update_status(self, document, status, error_message=None):
        document.status = status
        document.error_message = error_message
        return document

    async def rename(self, document, filename):
        document.filename = filename
        return document

    async def bump_version(self, document):
        document.version += 1
        return document

    async def delete(self, document):
        self.documents.pop(document.id, None)

    async def replace_chunks(self, document_id, chunks):
        pass


class FakeDocumentService(DocumentService):
    """Bypasses real file I/O and the ingestion pipeline; just marks the
    document INDEXED so upload() can be exercised through the API layer
    without touching disk or loading ML models."""

    def __init__(self, repo, fail_on_filename: str | None = None):
        super().__init__(repo)
        self._fail_on_filename = fail_on_filename

    async def upload(self, owner_id, filename, file_bytes):
        if self._fail_on_filename and filename == self._fail_on_filename:
            raise DocumentServiceError("Simulated ingestion failure")
        document = await self._documents.create(
            owner_id=owner_id,
            filename=filename,
            file_type=DocumentType.TXT if filename.endswith(".txt") else DocumentType.PDF,
            file_path="/tmp/fake",
            file_size_bytes=len(file_bytes),
        )
        await self._documents.update_status(document, DocumentStatus.INDEXED)
        return document


@pytest.fixture
def fake_user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def fake_document_repo() -> FakeDocumentRepository:
    return FakeDocumentRepository()


@pytest.fixture
def client(fake_user_repo, fake_document_repo) -> TestClient:
    app.dependency_overrides[get_auth_service] = lambda: AuthService(fake_user_repo)
    app.dependency_overrides[get_user_repository] = lambda: fake_user_repo
    app.dependency_overrides[get_document_repository] = lambda: fake_document_repo
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService(fake_document_repo)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    client.post(
        f"{settings.API_V1_PREFIX}/auth/register",
        json={"email": "docs@example.com", "full_name": "Docs User", "password": "password123"},
    )
    login = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"email": "docs@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.api
class TestUploadEndpoint:
    def test_upload_requires_auth(self, client: TestClient):
        response = client.post(PREFIX, files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")})
        assert response.status_code == 401

    def test_upload_success(self, client: TestClient, auth_headers: dict):
        response = client.post(
            PREFIX,
            files={"file": ("test.txt", io.BytesIO(b"hello world"), "text/plain")},
            headers=auth_headers,
        )
        assert response.status_code == 201
        body = response.json()
        assert body["filename"] == "test.txt"
        assert body["status"] == "indexed"


@pytest.mark.api
class TestListAndGetEndpoints:
    def test_list_documents(self, client: TestClient, auth_headers: dict):
        client.post(
            PREFIX,
            files={"file": ("a.txt", io.BytesIO(b"content a"), "text/plain")},
            headers=auth_headers,
        )
        response = client.get(PREFIX, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_get_document_not_found(self, client: TestClient, auth_headers: dict):
        response = client.get(f"{PREFIX}/{uuid.uuid4()}", headers=auth_headers)
        assert response.status_code == 404

    def test_get_document_success(self, client: TestClient, auth_headers: dict):
        upload = client.post(
            PREFIX,
            files={"file": ("b.txt", io.BytesIO(b"content b"), "text/plain")},
            headers=auth_headers,
        )
        doc_id = upload.json()["id"]
        response = client.get(f"{PREFIX}/{doc_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["filename"] == "b.txt"


@pytest.mark.api
class TestRenameAndDeleteEndpoints:
    def test_rename_document(self, client: TestClient, auth_headers: dict):
        upload = client.post(
            PREFIX,
            files={"file": ("c.txt", io.BytesIO(b"content c"), "text/plain")},
            headers=auth_headers,
        )
        doc_id = upload.json()["id"]
        response = client.patch(f"{PREFIX}/{doc_id}", json={"filename": "renamed.txt"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["filename"] == "renamed.txt"

    def test_delete_document(self, client: TestClient, auth_headers: dict):
        upload = client.post(
            PREFIX,
            files={"file": ("d.txt", io.BytesIO(b"content d"), "text/plain")},
            headers=auth_headers,
        )
        doc_id = upload.json()["id"]
        response = client.delete(f"{PREFIX}/{doc_id}", headers=auth_headers)
        assert response.status_code == 204

        follow_up = client.get(f"{PREFIX}/{doc_id}", headers=auth_headers)
        assert follow_up.status_code == 404
