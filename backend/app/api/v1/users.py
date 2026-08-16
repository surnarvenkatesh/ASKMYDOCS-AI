"""
User profile endpoints — all require a valid access token.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_user_repository
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead, summary="Get my profile")
async def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.patch("/me", response_model=UserRead, summary="Update my profile")
async def update_my_profile(
    updates: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    fields = {"full_name": updates.full_name}
    if updates.password:
        fields["hashed_password"] = hash_password(updates.password)

    updated_user = await user_repository.update(current_user, **fields)
    await db.commit()
    return updated_user
