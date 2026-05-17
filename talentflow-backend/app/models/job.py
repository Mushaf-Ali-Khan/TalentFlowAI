from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel

class Job(BaseModel):
    __tablename__ = "jobs"

    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    requirements = Column(JSON, nullable=False, default={})
    scoring_rubric = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default='draft')
    embedding = Column(Vector())
    embedding_model_ver = Column(String)

    organization = relationship("Organization")
    creator = relationship("User")
