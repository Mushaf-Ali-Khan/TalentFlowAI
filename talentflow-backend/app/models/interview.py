from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class Interview(BaseModel):
    __tablename__ = "interviews"

    candidate_id = Column(UUID(as_uuid=True), ForeignKey('candidates.id'), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    scheduled_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=60)
    format = Column(String, nullable=False) # 'video'|'phone'|'in_person'
    meeting_link = Column(String)
    notes = Column(String)
    status = Column(String, nullable=False, default='scheduled')

    candidate = relationship("Candidate")
    job = relationship("Job")
    organization = relationship("Organization")
    scheduler = relationship("User")
