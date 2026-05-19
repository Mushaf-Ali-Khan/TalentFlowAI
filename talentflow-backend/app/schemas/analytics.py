from pydantic import BaseModel

class AnalyticsOverview(BaseModel):
    total_candidates: int
    avg_total_score: float
    avg_semantic_score: float
    pass_rate: float
    active_jobs: int
    score_distribution: dict[str, int]
