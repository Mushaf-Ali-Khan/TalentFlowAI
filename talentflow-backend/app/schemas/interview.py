from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class InterviewCreate(BaseModel):
    candidate_id: UUID
    job_id: UUID
    scheduled_at: datetime
    duration_minutes: int = 60
    format: str = "video"  # 'video'|'phone'|'in_person'
    meeting_link: Optional[str] = None
    notes: Optional[str] = None

class InterviewUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    format: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None # 'scheduled'|'completed'|'cancelled'

class InterviewResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID
    org_id: UUID
    scheduled_by: UUID
    scheduled_at: datetime
    duration_minutes: int
    format: str
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InterviewDetailsResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    candidate_name: str
    candidate_email: str
    job_id: UUID
    job_title: str
    scheduled_at: datetime
    duration_minutes: int
    format: str
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
