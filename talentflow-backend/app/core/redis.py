import logging
from typing import Optional

from redis.asyncio import Redis
from app.config import settings

logger = logging.getLogger(__name__)

# For FastAPI (lifespan-managed)
redis_client: Optional[Redis] = None

class NoopRedis:
    async def get(self, key):
        return None

    async def setex(self, key, ttl, val):
        return None

async def init_redis() -> None:
    global redis_client
    try:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}")
        redis_client = None

async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

async def get_redis():
    """
    Return a Redis client.
    For FastAPI: uses the lifespan-managed global client.
    For Celery workers: creates a fresh connection each time to avoid
    event-loop-mismatch issues.
    """
    if redis_client:
        return redis_client
    
    # If no global client (e.g., we're in a Celery worker), create one on-the-fly
    try:
        client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis unavailable in worker: {e}")
        return NoopRedis()
