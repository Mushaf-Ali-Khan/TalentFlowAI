import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
