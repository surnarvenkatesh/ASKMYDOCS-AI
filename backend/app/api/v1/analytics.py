"""
Analytics endpoints — usage dashboard summary for the current user.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_analytics_service, get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary, summary="Get usage analytics summary")
async def get_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    analytics_service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    days: int = Query(default=14, ge=1, le=90),
) -> dict:
    return await analytics_service.get_summary(current_user.id, days=days)
