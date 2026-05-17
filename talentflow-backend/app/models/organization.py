from sqlalchemy import Column, String, JSON
from .base import BaseModel

class Organization(BaseModel):
    __tablename__ = "organizations"

    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    clerk_org_id = Column(String, unique=True, nullable=False)
    plan = Column(String, nullable=False, default='starter')
    settings = Column(JSON, nullable=False, default={})
