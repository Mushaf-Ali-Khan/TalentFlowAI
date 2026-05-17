from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class Shortlist(BaseModel):
    __tablename__ = "shortlists"

    batch_id = Column(UUID(as_uuid=True), ForeignKey('batches.id'), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('candidates.id'), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('jobs.id'), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    rank = Column(Integer, nullable=False)

    batch = relationship("Batch")
    candidate = relationship("Candidate")
    job = relationship("Job")
    organization = relationship("Organization")
