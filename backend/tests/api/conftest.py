"""
Shared fixtures for API-level tests.

API tests override `get_auth_service` with a service backed by the same
in-memory fake repository used in the unit tests, so route wiring,
status codes, and response schemas can be verified without a live
Postgres instance. True end-to-end DB behavior is covered separately by
the `integration` marked tests, which run against docker-compose's db.
"""
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_auth_service, get_user_repository
from app.main import app
from tests.unit.test_auth_service import FakeUserRepository
from app.services.auth_service import AuthService


@pytest.fixture
def fake_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def client(fake_repo: FakeUserRepository) -> TestClient:
    # Both overrides share the same fake_repo instance so a user registered
    # via AuthService is visible to get_current_user's lookup, and vice versa.
    app.dependency_overrides[get_auth_service] = lambda: AuthService(fake_repo)
    app.dependency_overrides[get_user_repository] = lambda: fake_repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
