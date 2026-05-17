from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class Batch(BaseModel):
    __tablename__ = "batches"

    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    idempotency_key = Column(String, unique=True)
    status = Column(String, nullable=False, default='queued')
    total_cvs = Column(Integer, nullable=False, default=0)
    processed_cvs = Column(Integer, nullable=False, default=0)
    failed_cvs = Column(Integer, nullable=False, default=0)
    error_summary = Column(JSON)
    celery_task_id = Column(String)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    organization = relationship("Organization")
    job = relationship("Job")
    submitter = relationship("User")
