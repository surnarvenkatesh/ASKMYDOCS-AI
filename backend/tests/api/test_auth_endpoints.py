"""
API tests for /api/v1/auth/* — exercise route wiring, validation, and
status codes through FastAPI's TestClient.
"""
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

PREFIX = f"{settings.API_V1_PREFIX}/auth"


@pytest.mark.api
class TestRegisterEndpoint:
    def test_register_success(self, client: TestClient):
        response = client.post(
            f"{PREFIX}/register",
            json={"email": "api@example.com", "full_name": "API User", "password": "password123"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "api@example.com"
        assert "hashed_password" not in body

    def test_register_duplicate_email_returns_409(self, client: TestClient):
        payload = {"email": "dup@example.com", "full_name": "Dup", "password": "password123"}
        client.post(f"{PREFIX}/register", json=payload)
        response = client.post(f"{PREFIX}/register", json=payload)
        assert response.status_code == 409

    def test_register_rejects_short_password(self, client: TestClient):
        response = client.post(
            f"{PREFIX}/register",
            json={"email": "short@example.com", "full_name": "Short", "password": "123"},
        )
        assert response.status_code == 422

    def test_register_rejects_invalid_email(self, client: TestClient):
        response = client.post(
            f"{PREFIX}/register",
            json={"email": "not-an-email", "full_name": "Bad", "password": "password123"},
        )
        assert response.status_code == 422


@pytest.mark.api
class TestLoginEndpoint:
    def _register(self, client: TestClient, email: str, password: str):
        client.post(
            f"{PREFIX}/register",
            json={"email": email, "full_name": "Login User", "password": password},
        )

    def test_login_success(self, client: TestClient):
        self._register(client, "login@example.com", "password123")
        response = client.post(
            f"{PREFIX}/login", json={"email": "login@example.com", "password": "password123"}
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body and "refresh_token" in body

    def test_login_wrong_password_returns_401(self, client: TestClient):
        self._register(client, "login2@example.com", "password123")
        response = client.post(
            f"{PREFIX}/login", json={"email": "login2@example.com", "password": "wrong"}
        )
        assert response.status_code == 401


@pytest.mark.api
class TestMeEndpoint:
    def test_me_requires_auth(self, client: TestClient):
        response = client.get(f"{PREFIX}/me")
        assert response.status_code == 401

    def test_me_returns_profile_with_valid_token(self, client: TestClient):
        client.post(
            f"{PREFIX}/register",
            json={"email": "me@example.com", "full_name": "Me", "password": "password123"},
        )
        login = client.post(
            f"{PREFIX}/login", json={"email": "me@example.com", "password": "password123"}
        )
        token = login.json()["access_token"]
        response = client.get(f"{PREFIX}/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"

    def test_me_rejects_garbage_token(self, client: TestClient):
        response = client.get(f"{PREFIX}/me", headers={"Authorization": "Bearer garbage"})
        assert response.status_code == 401


@pytest.mark.api
class TestHealthEndpoint:
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
