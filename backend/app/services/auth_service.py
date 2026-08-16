"""
Auth service: business logic for registration, login, and token refresh.

Depends only on the repository abstraction (dependency inversion), so it
can be unit tested with a fake repository with no real database.
"""
import uuid

from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate


class AuthError(Exception):
    """Raised for any auth failure the API layer should turn into a 4xx."""


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def register(self, user_in: UserCreate) -> User:
        existing = await self._users.get_by_email(user_in.email)
        if existing is not None:
            raise AuthError("A user with this email already exists")

        hashed = hash_password(user_in.password)
        return await self._users.create(user_in, hashed_password=hashed)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthError("Incorrect email or password")
        if not user.is_active:
            raise AuthError("This account has been deactivated")
        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.authenticate(email, password)
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh_access_token(self, refresh_token: str) -> str:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except TokenError as exc:
            raise AuthError(str(exc)) from exc

        user_id = uuid.UUID(payload["sub"])
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthError("User not found or inactive")

        return create_access_token(user.id)
