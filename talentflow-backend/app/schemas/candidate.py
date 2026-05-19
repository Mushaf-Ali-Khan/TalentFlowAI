import json
from pydantic import BaseModel, EmailStr, AnyUrl, ConfigDict, field_validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

class SkillEntry(BaseModel):
    name:               str
    years_experience:   Optional[float] = None
    proficiency:        Optional[str] = None

class ExperienceEntry(BaseModel):
    company:            str
    title:              str
    start_date:         date
    end_date:           Optional[date] = None
    is_current:         bool = False
    description:        Optional[str] = None
    achievements:       List[str] = []

class EducationEntry(BaseModel):
    institution:        str
    degree:             Optional[str] = None
    field:              Optional[str] = None
    graduation_year:    Optional[int] = None

class CandidateProfile(BaseModel):
    model_config = ConfigDict(strict=True)
    
    name:                       Optional[str] = None
    email:                      Optional[EmailStr] = None
    phone:                      Optional[str] = None
    location:                   Optional[str] = None
    linkedin_url:               Optional[AnyUrl] = None
    
    skills:                     List[SkillEntry] = []
    experience:                 List[ExperienceEntry] = []
    education:                  List[EducationEntry] = []
    certifications:             List[str] = []
    languages:                  List[str] = []
    
    total_years_experience:     float = 0.0
    seniority_level:            str = 'unknown'
    
    extraction_confidence:      float = 0.0
    needs_manual_review:        bool = False

class DimensionScore(BaseModel):
    score:          int
    justification:  str
    weight_bps:     int

class ScoringResult(BaseModel):
    skills_match:           DimensionScore
    experience_relevance:   DimensionScore
    education_fit:          DimensionScore
    growth_trajectory:      DimensionScore
    llm_score:              float
    overall_recommendation: str
    outlier_flag:           bool

class BiasAuditResult(BaseModel):
    name_detected: bool = False
    graduation_year_detected: bool = False
    location_detected: bool = False
    pronouns_detected: bool = False
    raw_text_excerpt: Optional[str] = None

class CandidateResponse(BaseModel):
    id: UUID
    org_id: UUID
    job_id: UUID
    batch_id: UUID
    r2_key: str
    original_filename: str
    file_size_bytes: int
    profile: Optional[dict] = None
    extraction_confidence: Optional[float] = None
    needs_manual_review: bool
    semantic_score: Optional[float] = None
    llm_score: Optional[float] = None
    total_score: Optional[float] = None
    score_breakdown: Optional[dict] = None
    auto_rejected: bool
    processing_status: str
    recruiter_status: Optional[str] = None
    recruiter_note: Optional[str] = None
    status_updated_by: Optional[UUID] = None
    status_updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

    @field_validator("profile", "score_breakdown", mode="before")
    @classmethod
    def _parse_json_fields(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return None
        return value
