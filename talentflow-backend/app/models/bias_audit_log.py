from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class BiasAuditLog(BaseModel):
    __tablename__ = "bias_audit_log"

    candidate_id = Column(UUID(as_uuid=True), ForeignKey('candidates.id'), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    detected_signals = Column(JSON, nullable=False)
    raw_text_excerpt = Column(String)

    candidate = relationship("Candidate")
    organization = relationship("Organization")
