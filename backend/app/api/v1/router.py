"""
Aggregates all v1 API routers into a single router mounted by main.py.
"""
from fastapi import APIRouter

from app.api.v1 import analytics, auth, chat, documents, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(analytics.router)
