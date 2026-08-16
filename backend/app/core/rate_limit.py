"""
Redis-backed rate limiting middleware.

Uses a fixed-window counter per (client identifier, minute bucket) —
simple, cheap on Redis, and good enough to stop abuse without the
complexity of a sliding-window log. Falls back to allowing the request
if Redis is unreachable (fail-open) rather than taking the whole API
down because the rate limiter's backing store is unavailable.
"""
from __future__ import annotations

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Requests allowed per identifier per 60-second window.
_DEFAULT_LIMIT = 120
# Auth endpoints get a stricter limit — they're the most valuable to abuse.
_AUTH_LIMIT = 20


def _limit_for_path(path: str) -> int:
    if path.endswith(("/auth/login", "/auth/register", "/auth/refresh")):
        return _AUTH_LIMIT
    return _DEFAULT_LIMIT


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client=None) -> None:
        super().__init__(app)
        self._redis = redis_client

    async def _get_redis(self):
        if self._redis is not None:
            return self._redis
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        identifier = request.headers.get("Authorization", request.client.host if request.client else "anonymous")
        window = int(time.time() // 60)
        key = f"ratelimit:{identifier}:{window}"
        limit = _limit_for_path(request.url.path)

        try:
            redis_client = await self._get_redis()
            current = await redis_client.incr(key)
            if current == 1:
                await redis_client.expire(key, 60)
        except Exception as exc:  # noqa: BLE001 — fail open, log and continue
            logger.warning("rate_limit_backend_unavailable", error=str(exc))
            return await call_next(request)

        if current > limit:
            return Response(
                content='{"detail":"Too many requests. Please slow down."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        return await call_next(request)
