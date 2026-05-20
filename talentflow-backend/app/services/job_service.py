from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.job_repo import job_repo
from app.models.job import Job
from app.utils.embeddings import embedding_service
from app.core.redis import get_redis
from app.config import settings
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)

DEFAULT_SCORING_RUBRIC = {
    "skills_match": 4000,
    "experience_relevance": 3000,
    "education_fit": 1500,
    "growth_trajectory": 1500,
}

class JobService:
    def _normalize_scoring_rubric(self, rubric: Dict | None) -> Dict:
        if not rubric or not isinstance(rubric, dict):
            return DEFAULT_SCORING_RUBRIC.copy()
        merged = DEFAULT_SCORING_RUBRIC.copy()
        for key, value in rubric.items():
            if isinstance(value, int) and value > 0:
                merged[key] = value
        return merged

    def _build_embedding_text(self, description: str, requirements: Dict) -> str:
        req_text = json.dumps(requirements) if requirements else "{}"
        return f"Job Description: {description}\nRequirements: {req_text}"

    async def create_job(self, db: AsyncSession, job_data: dict, org_id: str, user_id: str) -> Job:
        job_data['org_id'] = org_id
        job_data['created_by'] = user_id
        job_data['requirements'] = job_data.get('requirements') or {}
        job_data['scoring_rubric'] = self._normalize_scoring_rubric(job_data.get('scoring_rubric'))

        try:
            embedding_text = self._build_embedding_text(job_data['description'], job_data['requirements'])
            vector = embedding_service.encode(embedding_text)
            job_data['embedding'] = vector
            job_data['embedding_model_ver'] = embedding_service.version
            logger.info(f"Job embedding generated: {len(vector)}-dim vector")
        except Exception as e:
            import traceback
            logger.error(f"Failed to build job embedding: {e}\n{traceback.format_exc()}")

        job = await job_repo.create(db, job_data)
        if job.embedding and job.embedding_model_ver:
            try:
                redis = await get_redis()
                cache_key = f"job_embedding:{job.id}:{job.embedding_model_ver}"
                await redis.setex(
                    cache_key,
                    settings.JOB_EMBEDDING_CACHE_TTL_SECONDS,
                    json.dumps(list(job.embedding))
                )
            except Exception as e:
                logger.warning(f"Failed to cache job embedding for {job.id}: {e}")
        return job

    async def get_jobs_for_org(self, db: AsyncSession, org_id: str, skip: int = 0, limit: int = 100) -> List[Job]:
        return await job_repo.get_by_org(db, org_id, skip, limit)

    async def get_job(self, db: AsyncSession, job_id: str) -> Job:
        return await job_repo.get(db, job_id)

job_service = JobService()
