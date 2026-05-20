"""
Backfill embeddings for jobs that are missing them.
Run: .venv\Scripts\python.exe backfill_job_embeddings.py
"""
import asyncio
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load env
from dotenv import load_dotenv
load_dotenv(".env.local")

from app.core.database import async_session
from app.utils.embeddings import embedding_service
from sqlalchemy import text

async def main():
    # 1. Test embedding model loads
    logger.info("Loading embedding model...")
    try:
        test_vec = embedding_service.encode("test embedding model")
        logger.info(f"Embedding model loaded OK — produces {len(test_vec)}-dim vectors")
    except Exception as e:
        logger.error(f"Embedding model failed to load: {e}")
        sys.exit(1)

    # 2. Find jobs missing embeddings
    async with async_session() as session:
        result = await session.execute(
            text("SELECT id, title, description, requirements FROM jobs WHERE embedding IS NULL")
        )
        jobs = result.fetchall()

    if not jobs:
        logger.info("All jobs already have embeddings — nothing to backfill.")
        return

    logger.info(f"Found {len(jobs)} jobs missing embeddings")

    for job_id, title, description, requirements in jobs:
        logger.info(f"  Embedding job: {title} ({job_id})")
        
        req_text = json.dumps(requirements) if requirements else "{}"
        embedding_text = f"Job Description: {description}\nRequirements: {req_text}"
        
        vector = embedding_service.encode(embedding_text)
        model_ver = embedding_service.version
        
        # pgvector expects a string like '[0.1, 0.2, ...]' cast to vector type
        vector_str = "[" + ",".join(str(v) for v in vector) + "]"
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    text("""
                        UPDATE jobs 
                        SET embedding = CAST(:embedding AS vector),
                            embedding_model_ver = :model_ver
                        WHERE id = :id
                    """),
                    {
                        "embedding": vector_str,
                        "model_ver": model_ver,
                        "id": str(job_id)
                    }
                )
        logger.info(f"  ✓ Done ({len(vector)}-dim vector)")

    logger.info(f"Backfilled {len(jobs)} jobs successfully!")

if __name__ == "__main__":
    asyncio.run(main())
