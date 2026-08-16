"""
Unit tests for app.services.auth_service.AuthService using a fake
in-memory UserRepository — validates business logic in isolation from
SQLAlchemy/Postgres.
"""
import uuid

import pytest

from app.core.security import create_refresh_token, hash_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import AuthError, AuthService


class FakeUserRepository:
    """In-memory stand-in for UserRepository, matching its public interface."""

    def __init__(self):
        self._by_id: dict[uuid.UUID, User] = {}

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._by_id.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._by_id.values() if u.email == email), None)

    async def create(self, user_in: UserCreate, hashed_password: str) -> User:
        user = User(
            id=uuid.uuid4(),
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        self._by_id[user.id] = user
        return user

    async def update(self, user: User, **fields) -> User:
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        return user


@pytest.fixture
def repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def service(repo: FakeUserRepository) -> AuthService:
    return AuthService(repo)


@pytest.mark.unit
class TestRegister:
    async def test_register_creates_user(self, service: AuthService):
        user = await service.register(
            UserCreate(email="new@example.com", full_name="New User", password="password123")
        )
        assert user.email == "new@example.com"
        assert user.hashed_password != "password123"

    async def test_register_rejects_duplicate_email(self, service: AuthService):
        payload = UserCreate(email="dup@example.com", full_name="Dup", password="password123")
        await service.register(payload)
        with pytest.raises(AuthError, match="already exists"):
            await service.register(payload)


@pytest.mark.unit
class TestLogin:
    async def test_login_succeeds_with_correct_credentials(self, service: AuthService):
        await service.register(
            UserCreate(email="user@example.com", full_name="User", password="correcthorse")
        )
        tokens = await service.login("user@example.com", "correcthorse")
        assert tokens.access_token
        assert tokens.refresh_token

    async def test_login_fails_with_wrong_password(self, service: AuthService):
        await service.register(
            UserCreate(email="user2@example.com", full_name="User", password="correcthorse")
        )
        with pytest.raises(AuthError, match="Incorrect email or password"):
            await service.login("user2@example.com", "wrongpassword")

    async def test_login_fails_for_unknown_email(self, service: AuthService):
        with pytest.raises(AuthError):
            await service.login("ghost@example.com", "whatever")

    async def test_login_fails_for_inactive_user(self, service: AuthService, repo: FakeUserRepository):
        user = await service.register(
            UserCreate(email="inactive@example.com", full_name="User", password="correcthorse")
        )
        user.is_active = False
        with pytest.raises(AuthError, match="deactivated"):
            await service.login("inactive@example.com", "correcthorse")


@pytest.mark.unit
class TestRefresh:
    async def test_refresh_issues_new_access_token(self, service: AuthService):
        user = await service.register(
            UserCreate(email="refresh@example.com", full_name="User", password="password123")
        )
        refresh_token = create_refresh_token(user.id)
        access_token = await service.refresh_access_token(refresh_token)
        assert access_token

    async def test_refresh_rejects_invalid_token(self, service: AuthService):
        with pytest.raises(AuthError):
            await service.refresh_access_token("not-a-token")

    async def test_refresh_rejects_unknown_user(self, service: AuthService):
        refresh_token = create_refresh_token(uuid.uuid4())
        with pytest.raises(AuthError, match="not found"):
            await service.refresh_access_token(refresh_token)
