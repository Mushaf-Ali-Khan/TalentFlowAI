from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str
    size_bytes: int

class UploadUrlResponseItem(BaseModel):
    filename: str
    upload_url: str
    r2_key: str

class BatchSubmitRequest(BaseModel):
    job_id: UUID
    r2_keys: List[str]
    idempotency_key: Optional[str] = None

class BatchStatusResponse(BaseModel):
    id: UUID
    status: str
    total_cvs: int
    processed_cvs: int
    failed_cvs: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
