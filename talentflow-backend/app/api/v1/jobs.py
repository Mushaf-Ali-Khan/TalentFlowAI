from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.common import SuccessResponse
from app.schemas.job import JobCreate, JobResponse
from app.schemas.candidate import CandidateResponse
from app.services.job_service import job_service
from app.services.user_service import user_service
from app.core.auth import get_current_user, ClerkUser
from app.core.rbac import require_recruiter
from app.core.database import get_db
from app.models.candidate import Candidate
from sqlalchemy import select, desc
from sqlalchemy.sql import nullslast

router = APIRouter()

@router.post("", response_model=SuccessResponse[JobResponse])
async def create_job(
    request: Request,
    job_in: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(require_recruiter)
):
    db_user = await user_service.get_or_create(db, current_user)
    job = await job_service.create_job(
        db=db,
        job_data=job_in.model_dump(),
        org_id=str(current_user.org_id),
        user_id=str(db_user.id)
    )
    return {"success": True, "data": job, "request_id": request.state.request_id}

@router.get("", response_model=SuccessResponse[List[JobResponse]])
async def list_jobs(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    jobs = await job_service.get_jobs_for_org(db, str(current_user.org_id))
    return {"success": True, "data": jobs, "request_id": request.state.request_id}

@router.get("/{job_id}", response_model=SuccessResponse[JobResponse])
async def get_job(
    job_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    job = await job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"success": True, "data": job, "request_id": request.state.request_id}

@router.get("/{job_id}/candidates", response_model=SuccessResponse[List[CandidateResponse]])
async def list_job_candidates(
    job_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    result = await db.execute(
        select(Candidate)
        .where(Candidate.job_id == job_id)
        .order_by(nullslast(desc(Candidate.total_score)))
    )
    candidates = list(result.scalars().all())
    return {"success": True, "data": candidates, "request_id": request.state.request_id}

