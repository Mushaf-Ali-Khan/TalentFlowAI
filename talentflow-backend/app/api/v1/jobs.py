from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.common import SuccessResponse
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import job_service
from app.core.auth import get_current_user, ClerkUser
from app.core.rbac import require_recruiter

# Needs a get_db dependency
async def get_db():
    from tests.conftest import async_session
    async with async_session() as session:
        yield session

router = APIRouter()

@router.post("", response_model=SuccessResponse[JobResponse])
async def create_job(
    request: Request,
    job_in: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(require_recruiter)
):
    job = await job_service.create_job(
        db=db,
        job_data=job_in.model_dump(),
        org_id=str(current_user.org_id),
        user_id=current_user.clerk_user_id
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

@router.get("/{job_id}/candidates")
async def list_job_candidates(
    job_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    from sqlalchemy import text
    import json
    
    result = await db.execute(
        text("SELECT * FROM candidates WHERE job_id = :job_id ORDER BY total_score DESC"),
        {"job_id": job_id}
    )
    rows = result.fetchall()
    
    candidates_list = []
    for r in rows:
        row_dict = dict(r._mapping)
        # Parse json fields if they are stored as strings in SQLite or select DB drivers
        if isinstance(row_dict.get("profile"), str):
            try:
                row_dict["profile"] = json.loads(row_dict["profile"])
            except Exception:
                pass
        if isinstance(row_dict.get("score_breakdown"), str):
            try:
                row_dict["score_breakdown"] = json.loads(row_dict["score_breakdown"])
            except Exception:
                pass
        candidates_list.append(row_dict)
        
    return {"success": True, "data": candidates_list, "request_id": request.state.request_id}

