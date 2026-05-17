import logging
import json
import math
from typing import List
from app.agents.state import PipelineState
from app.config import settings

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
        # We would inject redis client here, using a placeholder for now
        pass
        
    async def _get_job_embedding(self, job_id: str, model_ver: str) -> List[float]:
        # Placeholder for Redis cache hit and DB fallback
        # redis_key = f"jd_embedding:{job_id}:{model_ver}"
        logger.info(f"Fetching job embedding for job {job_id}")
        # In reality: await redis.get(redis_key), if miss: fetch from DB, cache and return
        
        # We return a dummy vector for testing
        return [0.1] * 1024

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
