from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: Dict = {}
    scoring_rubric: Dict[str, int]

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict] = None
    scoring_rubric: Optional[Dict[str, int]] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: UUID
    title: str
    description: str
    requirements: Dict
    scoring_rubric: Dict[str, int]
    status: str
    
    class Config:
        from_attributes = True
