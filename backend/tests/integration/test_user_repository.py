"""
Integration tests — require a live Postgres instance (e.g. via
`docker compose up db`) reachable at the DATABASE_URL env var.

Run explicitly with: pytest -m integration
These are excluded from the default fast test run.
"""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, Base, engine
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


@pytest.fixture(scope="module", autouse=True)
async def _setup_schema():
    """Create tables once for the integration test module, drop afterwards."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.mark.integration
class TestUserRepositoryIntegration:
    async def test_create_and_fetch_user(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        user = await repo.create(
            UserCreate(email=f"{uuid.uuid4()}@example.com", full_name="Integration User", password="x"),
            hashed_password="hashed",
        )
        await db_session.commit()

        fetched = await repo.get_by_id(user.id)
        assert fetched is not None
        assert fetched.email == user.email

    async def test_get_by_email_returns_none_when_missing(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        result = await repo.get_by_email("nobody@example.com")
        assert result is None
