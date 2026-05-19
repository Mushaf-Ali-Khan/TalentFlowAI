import asyncio
import logging
from typing import List, Dict, Any
from uuid import UUID
from celery.exceptions import SoftTimeLimitExceeded

from app.workers.celery_app import app
from app.agents.graph import create_pipeline_graph
from app.agents.state import PipelineState
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_session
from app.config import settings

logger = logging.getLogger(__name__)

# Note: Checkpointing is required in the spec using AsyncPostgresSaver
# For simplification in this prototype we can mock checkpointer or use it if fully implemented
# From langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

@app.task(bind=True, max_retries=3)
def process_single_cv(self, candidate_id: str, batch_id: str, r2_key: str, file_type: str, job_id: str, org_id: str, request_id: str):
    """
    Process a single CV through the LangGraph pipeline
    """
    logger.info(f"Processing single CV {candidate_id} from batch {batch_id}")
    
    # Run the async LangGraph execution in a sync wrapper since Celery tasks are sync by default
    # If we wanted to run pure async, we could use a custom asyncio worker, but standard celery needs asyncio.run
    try:
        asyncio.run(_async_process_single_cv(candidate_id, batch_id, r2_key, file_type, job_id, org_id, request_id))
    except SoftTimeLimitExceeded:
        logger.error(f"Task soft time limit exceeded for candidate {candidate_id}")
        self.retry(exc=Exception("SoftTimeLimitExceeded"))
    except Exception as e:
        logger.error(f"Task failed for candidate {candidate_id}: {e}")
        self.retry(exc=e)

async def _async_process_single_cv(candidate_id: str, batch_id: str, r2_key: str, file_type: str, job_id: str, org_id: str, request_id: str):
    # Initialize state
    initial_state: PipelineState = {
        "candidate_id": UUID(candidate_id),
        "batch_id": UUID(batch_id),
        "org_id": UUID(org_id),
        "job_id": UUID(job_id),
        "r2_key": r2_key,
        "file_type": file_type,
        "request_id": request_id,
    }
    
    if settings.ENABLE_LANGGRAPH_CHECKPOINTS:
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            async with AsyncPostgresSaver.from_conn_string(settings.CELERY_DATABASE_URL) as checkpointer:
                graph = create_pipeline_graph(checkpointer)
                config = {"configurable": {"thread_id": candidate_id}}
                result = await graph.ainvoke(initial_state, config=config)
        except Exception as e:
            logger.warning(f"Checkpointing unavailable, running without it: {e}")
            graph = create_pipeline_graph()
            result = await graph.ainvoke(initial_state)
    else:
        graph = create_pipeline_graph()
        result = await graph.ainvoke(initial_state)
    logger.info(f"Finished pipeline for candidate {candidate_id}")

@app.task(bind=True)
def process_cv_batch(self, batch_id: str):
    """
    Process an entire CV batch by fanning out process_single_cv tasks
    """
    logger.info(f"Processing batch {batch_id}")
    try:
        asyncio.run(_async_process_batch(batch_id))
    except Exception as e:
        logger.error(f"Failed to process batch {batch_id}: {e}")
        self.retry(exc=e)

async def _async_process_batch(batch_id: str):
    async with async_session() as session:
        # Update batch status to processing
        await session.execute(
            text("UPDATE batches SET status = 'processing', started_at = NOW() WHERE id = :id"),
            {"id": batch_id}
        )
        
        # Get all candidates for this batch
        result = await session.execute(
            text("SELECT id, r2_key, original_filename, job_id, org_id FROM candidates WHERE batch_id = :batch_id"),
            {"batch_id": batch_id}
        )
        candidates = result.fetchall()
        await session.commit()
        
    for cand in candidates:
        file_type = cand.original_filename.split('.')[-1].lower() if '.' in cand.original_filename else 'pdf'
        # Enqueue individual task
        process_single_cv.delay(
            candidate_id=str(cand.id),
            batch_id=batch_id,
            r2_key=cand.r2_key,
            file_type=file_type,
            job_id=str(cand.job_id),
            org_id=str(cand.org_id),
            request_id=f"req-{cand.id}"
        )
    
    logger.info(f"Enqueued {len(candidates)} CV tasks for batch {batch_id}")
