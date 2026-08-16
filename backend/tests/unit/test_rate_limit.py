"""
Unit tests for app.core.rate_limit.RateLimitMiddleware, using a fake
async Redis client so no real Redis instance is needed.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.rate_limit import RateLimitMiddleware


class FakeRedis:
    def __init__(self):
        self.counts: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, seconds: int) -> None:
        pass


class BrokenRedis:
    async def incr(self, key: str) -> int:
        raise ConnectionError("redis unreachable")


def _make_app(redis_client) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, redis_client=redis_client)

    @app.get("/api/v1/documents")
    async def documents():
        return {"ok": True}

    @app.post("/api/v1/auth/login")
    async def login():
        return {"ok": True}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


@pytest.mark.unit
class TestRateLimitMiddleware:
    def test_requests_under_limit_pass_through(self):
        app = _make_app(FakeRedis())
        client = TestClient(app)
        for _ in range(5):
            response = client.get("/api/v1/documents")
            assert response.status_code == 200

    def test_exceeding_default_limit_returns_429(self):
        app = _make_app(FakeRedis())
        client = TestClient(app)
        for _ in range(120):
            client.get("/api/v1/documents")
        response = client.get("/api/v1/documents")
        assert response.status_code == 429
        assert "Retry-After" in response.headers

    def test_auth_endpoints_have_a_stricter_limit(self):
        app = _make_app(FakeRedis())
        client = TestClient(app)
        for _ in range(20):
            client.post("/api/v1/auth/login")
        response = client.post("/api/v1/auth/login")
        assert response.status_code == 429

    def test_health_endpoint_is_never_rate_limited(self):
        app = _make_app(FakeRedis())
        client = TestClient(app)
        for _ in range(200):
            response = client.get("/health")
            assert response.status_code == 200

    def test_redis_unavailable_fails_open(self):
        app = _make_app(BrokenRedis())
        client = TestClient(app)
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
