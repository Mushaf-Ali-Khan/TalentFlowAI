import logging
import json
import math
from typing import List
from app.agents.state import PipelineState
from app.config import settings
from app.core.database import async_session
from app.core.redis import get_redis
from app.models.job import Job
from sqlalchemy import select

logger = logging.getLogger(__name__)

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

class MatcherNode:
    """
    Node 4: Cosine similarity vs JD embedding
    """
    
    def __init__(self):
        pass
        
    async def _get_cached_embedding(self, cache_key: str) -> List[float]:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if not cached:
            return []
        try:
            return json.loads(cached)
        except Exception as e:
            logger.warning(f"Invalid cached embedding for {cache_key}: {e}")
            return []

    async def _get_job_embedding(self, job_id: str, model_ver: str) -> List[float]:
        logger.info(f"Fetching job embedding for job {job_id}")
        cache_key = f"job_embedding:{job_id}:{model_ver}"
        cached = await self._get_cached_embedding(cache_key)
        if cached:
            return cached

        async with async_session() as session:
            result = await session.execute(
                select(Job.embedding, Job.embedding_model_ver).where(Job.id == job_id)
            )
            row = result.first()

        if not row:
            return []

        embedding, stored_ver = row
        if stored_ver and model_ver and stored_ver != model_ver:
            logger.warning(
                f"Embedding model mismatch for job {job_id}: {stored_ver} != {model_ver}"
            )

        if embedding is None:
            return []

        if isinstance(embedding, str):
            try:
                embedding = json.loads(embedding)
            except Exception:
                return []

        embedding_list = list(embedding)
        try:
            redis = await get_redis()
            await redis.setex(cache_key, settings.JOB_EMBEDDING_CACHE_TTL_SECONDS, json.dumps(embedding_list))
        except Exception as e:
            logger.warning(f"Failed to cache job embedding for {job_id}: {e}")
        return embedding_list

    async def __call__(self, state: PipelineState) -> dict:
        logger.info(f"MatcherNode running for candidate {state.get('candidate_id')}")
        
        candidate_embedding = state.get("embedding")
        job_id = str(state.get("job_id"))
        model_ver = state.get("embedding_model_ver")
        
        if not candidate_embedding or not model_ver:
            return {
                "semantic_score": 0.0,
                "auto_rejected": False
            }

        try:
            job_embedding = await self._get_job_embedding(job_id, model_ver)
            
            if not job_embedding:
                logger.warning(f"No job embedding found for job {job_id}, skipping matcher")
                return {
                    "semantic_score": 0.0,
                    "auto_rejected": False
                }
                
            score = cosine_similarity(candidate_embedding, job_embedding)
            
            auto_reject = False
            if score < settings.AUTO_REJECT_THRESHOLD:
                auto_reject = True
                
            return {
                "semantic_score": score,
                "job_embedding": job_embedding,
                "auto_rejected": auto_reject
            }
            
        except Exception as e:
            logger.error(f"MatcherNode failed: {e}")
            return {
                "semantic_score": 0.0,
                "auto_rejected": False
            }
