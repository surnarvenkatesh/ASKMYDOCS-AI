"""
Request logging middleware — emits one structured log line per request
with a correlation id, so individual requests can be traced through
logs in production (and joined with error tracking / APM by request_id
if you wire one in).
"""
from __future__ import annotations

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.logging import get_logger

logger = get_logger("api.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())
        started_at = time.perf_counter()

        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            logger.info(
                "api_request",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code if response else 500,
                duration_ms=duration_ms,
                client_ip=request.client.host if request.client else None,
            )
            if response is not None:
                response.headers["X-Request-ID"] = request_id
