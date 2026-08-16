"""
API test for /api/v1/analytics/summary.
"""
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_analytics_service, get_auth_service, get_user_repository
from app.core.config import settings
from app.main import app
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from tests.unit.test_analytics_service import FakeAnalyticsRepository
from tests.unit.test_auth_service import FakeUserRepository

PREFIX = f"{settings.API_V1_PREFIX}/analytics"


@pytest.fixture
def client() -> TestClient:
    fake_user_repo = FakeUserRepository()
    fake_analytics_repo = FakeAnalyticsRepository(documents=2, chunks=10)

    app.dependency_overrides[get_auth_service] = lambda: AuthService(fake_user_repo)
    app.dependency_overrides[get_user_repository] = lambda: fake_user_repo
    app.dependency_overrides[get_analytics_service] = lambda: AnalyticsService(fake_analytics_repo)

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    client.post(
        f"{settings.API_V1_PREFIX}/auth/register",
        json={"email": "analytics@example.com", "full_name": "Analytics User", "password": "password123"},
    )
    login = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"email": "analytics@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.api
class TestAnalyticsSummaryEndpoint:
    def test_requires_auth(self, client: TestClient):
        response = client.get(f"{PREFIX}/summary")
        assert response.status_code == 401

    def test_returns_summary(self, client: TestClient, auth_headers: dict):
        response = client.get(f"{PREFIX}/summary", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["documents_count"] == 2
        assert body["embeddings_count"] == 10
        assert "daily_queries" in body
