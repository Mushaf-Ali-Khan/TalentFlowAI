from pydantic import BaseModel, EmailStr, AnyUrl, ConfigDict
from typing import Optional, List
from datetime import date

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
