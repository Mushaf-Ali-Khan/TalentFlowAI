from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.common import SuccessResponse
from app.schemas.candidate import CandidateResponse
from app.services.shortlist_service import shortlist_service
from app.core.auth import get_current_user, ClerkUser
from app.core.database import get_db

router = APIRouter()

@router.get("/batch/{batch_id}", response_model=SuccessResponse[List[CandidateResponse]])
async def get_shortlist_for_batch(
    batch_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    candidates = await shortlist_service.get_shortlist_for_batch(db, batch_id)
    return {"success": True, "data": candidates, "request_id": request.state.request_id}
