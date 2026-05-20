from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.schemas.common import SuccessResponse
from app.schemas.candidate import CandidateResponse
from app.services.candidate_service import candidate_service
from app.services.user_service import user_service
from app.core.auth import get_current_user, ClerkUser
from app.core.database import get_db

router = APIRouter()

class StatusUpdateSchema(BaseModel):
    status: str
    note: Optional[str] = None

@router.get("/{candidate_id}", response_model=SuccessResponse[CandidateResponse])
async def get_candidate(
    candidate_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    candidate = await candidate_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"success": True, "data": candidate, "request_id": request.state.request_id}

@router.patch("/{candidate_id}/status", response_model=SuccessResponse[CandidateResponse])
async def update_status(
    candidate_id: str,
    body: StatusUpdateSchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    db_user = await user_service.get_or_create(db, current_user)
    candidate = await candidate_service.update_status(
        db=db,
        candidate_id=candidate_id,
        status=body.status,
        note=body.note or "",
        user_id=str(db_user.id)
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"success": True, "data": candidate, "request_id": request.state.request_id}
