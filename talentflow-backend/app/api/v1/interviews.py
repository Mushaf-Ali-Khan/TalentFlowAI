from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc
from typing import List
from uuid import UUID

from app.schemas.common import SuccessResponse
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewDetailsResponse
from app.services.user_service import user_service
from app.core.auth import get_current_user, ClerkUser
from app.core.database import get_db
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.job import Job

router = APIRouter()

@router.get("", response_model=SuccessResponse[List[InterviewDetailsResponse]])
async def list_interviews(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    # Query interviews joining candidates and jobs
    stmt = (
        select(
            Interview,
            Candidate.name.label("candidate_name"),
            Candidate.profile.label("candidate_profile"),
            Job.title.label("job_title")
        )
        .join(Candidate, Interview.candidate_id == Candidate.id)
        .join(Job, Interview.job_id == Job.id)
        .where(Interview.org_id == current_user.org_id)
        .order_by(desc(Interview.scheduled_at))
    )
    
    res = await db.execute(stmt)
    records = res.all()
    
    data = []
    for row in records:
        interview, c_name, c_profile, j_title = row
        
        # Candidate name fallback
        name = c_name or (c_profile.get("name") if c_profile else None) or "Candidate"
        email = (c_profile.get("email") if c_profile else None) or "N/A"
        
        data.append({
            "id": interview.id,
            "candidate_id": interview.candidate_id,
            "candidate_name": name,
            "candidate_email": email,
            "job_id": interview.job_id,
            "job_title": j_title,
            "scheduled_at": interview.scheduled_at,
            "duration_minutes": interview.duration_minutes,
            "format": interview.format,
            "meeting_link": interview.meeting_link,
            "notes": interview.notes,
            "status": interview.status,
            "created_at": interview.created_at
        })
        
    return {"success": True, "data": data, "request_id": request.state.request_id}

@router.post("", response_model=SuccessResponse[InterviewDetailsResponse])
async def schedule_interview(
    request: Request,
    interview_in: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    db_user = await user_service.get_or_create(db, current_user)
    
    # Check if job and candidate exist
    job = await db.get(Job, interview_in.job_id)
    candidate = await db.get(Candidate, interview_in.candidate_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    # Create interview record
    db_interview = Interview(
        candidate_id=interview_in.candidate_id,
        job_id=interview_in.job_id,
        org_id=current_user.org_id,
        scheduled_by=db_user.id,
        scheduled_at=interview_in.scheduled_at,
        duration_minutes=interview_in.duration_minutes,
        format=interview_in.format,
        meeting_link=interview_in.meeting_link,
        notes=interview_in.notes,
        status="scheduled"
    )
    
    db.add(db_interview)
    await db.commit()
    await db.refresh(db_interview)
    
    # Build complete return details
    name = candidate.name or (candidate.profile.get("name") if candidate.profile else None) or "Candidate"
    email = (candidate.profile.get("email") if candidate.profile else None) or "N/A"
    
    detail = {
        "id": db_interview.id,
        "candidate_id": db_interview.candidate_id,
        "candidate_name": name,
        "candidate_email": email,
        "job_id": db_interview.job_id,
        "job_title": job.title,
        "scheduled_at": db_interview.scheduled_at,
        "duration_minutes": db_interview.duration_minutes,
        "format": db_interview.format,
        "meeting_link": db_interview.meeting_link,
        "notes": db_interview.notes,
        "status": db_interview.status,
        "created_at": db_interview.created_at
    }
    
    return {"success": True, "data": detail, "request_id": request.state.request_id}

@router.patch("/{interview_id}", response_model=SuccessResponse[InterviewDetailsResponse])
async def update_interview(
    interview_id: UUID,
    interview_update: InterviewUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    db_interview = await db.get(Interview, interview_id)
    if not db_interview or db_interview.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    update_data = interview_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_interview, key, value)
        
    await db.commit()
    await db.refresh(db_interview)
    
    # Reload info
    job = await db.get(Job, db_interview.job_id)
    candidate = await db.get(Candidate, db_interview.candidate_id)
    
    name = candidate.name or (candidate.profile.get("name") if candidate.profile else None) or "Candidate"
    email = (candidate.profile.get("email") if candidate.profile else None) or "N/A"
    
    detail = {
        "id": db_interview.id,
        "candidate_id": db_interview.candidate_id,
        "candidate_name": name,
        "candidate_email": email,
        "job_id": db_interview.job_id,
        "job_title": job.title if job else "N/A",
        "scheduled_at": db_interview.scheduled_at,
        "duration_minutes": db_interview.duration_minutes,
        "format": db_interview.format,
        "meeting_link": db_interview.meeting_link,
        "notes": db_interview.notes,
        "status": db_interview.status,
        "created_at": db_interview.created_at
    }
    
    return {"success": True, "data": detail, "request_id": request.state.request_id}

@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    db_interview = await db.get(Interview, interview_id)
    if not db_interview or db_interview.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    await db.delete(db_interview)
    await db.commit()
    
    return {"success": True, "data": {"message": "Interview cancelled successfully"}, "request_id": request.state.request_id}
