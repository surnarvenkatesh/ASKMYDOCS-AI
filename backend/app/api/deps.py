"""
Shared FastAPI dependencies: dependency-injects repositories, services,
and the currently authenticated user based on the Authorization header.
"""
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import TokenError, decode_token
from app.models.user import User
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository
from app.retrieval.embeddings import get_embedding_provider
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.llm_provider import get_llm_provider
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_analytics_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> AnalyticsRepository:
    return AnalyticsRepository(db)


def get_analytics_service(
    analytics_repository: Annotated[AnalyticsRepository, Depends(get_analytics_repository)],
) -> AnalyticsService:
    return AnalyticsService(analytics_repository)


def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_document_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> DocumentRepository:
    return DocumentRepository(db)


def get_conversation_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationRepository:
    return ConversationRepository(db)


def get_document_service(
    document_repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> DocumentService:
    return DocumentService(document_repository)


def get_hybrid_retriever(db: Annotated[AsyncSession, Depends(get_db)]) -> HybridRetriever:
    return HybridRetriever(db, get_embedding_provider())


def get_chat_service(
    conversation_repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    document_repository: Annotated[DocumentRepository, Depends(get_document_repository)],
    retriever: Annotated[HybridRetriever, Depends(get_hybrid_retriever)],
) -> ChatService:
    return ChatService(conversation_repository, document_repository, retriever, get_llm_provider())


def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(user_repository)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token, expected_type="access")
    except TokenError as exc:
        raise credentials_exception from exc

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise credentials_exception from exc

    user = await user_repository.get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges",
        )
    return current_user
