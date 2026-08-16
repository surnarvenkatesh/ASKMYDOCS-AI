"""
Unit test for app.core.request_logging.RequestLoggingMiddleware.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.request_logging import RequestLoggingMiddleware


@pytest.mark.unit
class TestRequestLoggingMiddleware:
    def test_attaches_request_id_header(self):
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/ping")
        async def ping():
            return {"ok": True}

        client = TestClient(app)
        response = client.get("/ping")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 36  # UUID4 string length

    def test_request_ids_are_unique_per_request(self):
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/ping")
        async def ping():
            return {"ok": True}

        client = TestClient(app)
        id_a = client.get("/ping").headers["X-Request-ID"]
        id_b = client.get("/ping").headers["X-Request-ID"]
        assert id_a != id_b
