from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import SuccessResponse
from app.schemas.analytics import AnalyticsOverview
from app.services.analytics_service import analytics_service
from app.core.auth import get_current_user, ClerkUser
from app.core.database import get_db

router = APIRouter()

@router.get("/overview", response_model=SuccessResponse[AnalyticsOverview])
async def get_overview(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    overview = await analytics_service.get_overview(db, str(current_user.org_id))
    return {"success": True, "data": overview, "request_id": request.state.request_id}
