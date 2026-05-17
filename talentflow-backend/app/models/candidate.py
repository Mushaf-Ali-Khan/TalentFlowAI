from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel

class Candidate(BaseModel):
    __tablename__ = "candidates"

    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey('batches.id'), nullable=False)
    
    r2_key = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_hash = Column(String, nullable=False)
    
    profile = Column(JSON)
    extraction_confidence = Column(Float)
    needs_manual_review = Column(Boolean, nullable=False, default=False)
    
    embedding = Column(Vector())
    embedding_model_ver = Column(String)
    
    semantic_score = Column(Float)
    llm_score = Column(Float)
    total_score = Column(Float)
    score_breakdown = Column(JSON)
    auto_rejected = Column(Boolean, nullable=False, default=False)
    
    processing_status = Column(String, nullable=False, default='pending')
    recruiter_status = Column(String)
    recruiter_note = Column(String)
    status_updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    status_updated_at = Column(DateTime(timezone=True))
    
    deleted_at = Column(DateTime(timezone=True))

    organization = relationship("Organization")
    job = relationship("Job")
    batch = relationship("Batch")
    status_updater = relationship("User")
