from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    clerk_user_id = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, nullable=False, default='recruiter')

    organization = relationship("Organization")
