import asyncio
import logging
import threading
from typing import List, Dict, Any
from uuid import UUID
from celery.exceptions import SoftTimeLimitExceeded

from app.workers.celery_app import app
from app.agents.graph import create_pipeline_graph
from app.agents.state import PipelineState
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Persistent event loop for the Celery worker process.
# Each asyncio.run() creates+destroys a loop, which kills SQLAlchemy's asyncpg
# connection pool (bound to the old loop). Instead, we keep ONE loop alive for
# the entire worker lifetime and schedule coroutines onto it.
# ---------------------------------------------------------------------------

_worker_loop: asyncio.AbstractEventLoop | None = None
_loop_thread: threading.Thread | None = None
_loop_lock = threading.Lock()


def _get_worker_loop() -> asyncio.AbstractEventLoop:
    """Return a persistent event loop running in a background daemon thread."""
    global _worker_loop, _loop_thread
    with _loop_lock:
        if _worker_loop is None or _worker_loop.is_closed():
            _worker_loop = asyncio.new_event_loop()
            _loop_thread = threading.Thread(
                target=_worker_loop.run_forever, daemon=True, name="celery-async-loop"
            )
            _loop_thread.start()
            logger.info("Started persistent async event loop for Celery worker")
    return _worker_loop


def run_async(coro):
    """Schedule a coroutine on the persistent worker loop and block until done."""
    loop = _get_worker_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()  # blocks the Celery thread until complete


# ---------------------------------------------------------------------------
# Fresh DB session factory for worker tasks.
# We create a separate engine so it binds to our persistent loop, not the
# (now-dead) loop from asyncio.run() that imported the module.
# ---------------------------------------------------------------------------

_worker_engine = None
_worker_session_factory = None
_engine_lock = threading.Lock()


def _get_worker_session() -> async_sessionmaker:
    """Lazily create a DB engine bound to the worker's persistent event loop."""
    global _worker_engine, _worker_session_factory
    with _engine_lock:
        if _worker_engine is None:
            _worker_engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=5,
            )
            _worker_session_factory = async_sessionmaker(
                _worker_engine, expire_on_commit=False, class_=AsyncSession
            )
            logger.info("Created worker-specific DB engine")
    return _worker_session_factory


# ---------------------------------------------------------------------------
# Celery tasks
# ---------------------------------------------------------------------------


@app.task(bind=True, max_retries=2, default_retry_delay=5)
def process_single_cv(self, candidate_id: str, batch_id: str, r2_key: str, file_type: str, job_id: str, org_id: str, request_id: str):
    """
    Process a single CV through the LangGraph pipeline.
    """
    logger.info(f"Processing single CV {candidate_id} from batch {batch_id}")

    try:
        run_async(_async_process_single_cv(candidate_id, batch_id, r2_key, file_type, job_id, org_id, request_id))
    except SoftTimeLimitExceeded:
        logger.error(f"Task soft time limit exceeded for candidate {candidate_id}")
        run_async(_mark_candidate_failed(candidate_id, batch_id, "Processing timed out"))
    except Exception as e:
        logger.error(f"Task failed for candidate {candidate_id} (attempt {self.request.retries + 1}): {e}")
        if self.request.retries < self.max_retries:
            self.retry(exc=e)
        else:
            logger.error(f"All retries exhausted for candidate {candidate_id}, marking as failed")
            try:
                run_async(_mark_candidate_failed(candidate_id, batch_id, str(e)))
            except Exception as mark_err:
                logger.error(f"Failed even to mark candidate as failed: {mark_err}")


async def _mark_candidate_failed(candidate_id: str, batch_id: str, error_msg: str):
    """Mark a candidate as failed and increment batch counter so batch can complete."""
    session_factory = _get_worker_session()
    try:
        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    text("UPDATE candidates SET processing_status = 'failed', updated_at = NOW() WHERE id = :id"),
                    {"id": candidate_id}
                )
                await session.execute(
                    text("UPDATE batches SET failed_cvs = failed_cvs + 1, processed_cvs = processed_cvs + 1 WHERE id = :id"),
                    {"id": batch_id}
                )
                # Check if batch is now complete
                result = await session.execute(
                    text("SELECT processed_cvs, total_cvs FROM batches WHERE id = :id"),
                    {"id": batch_id}
                )
                row = result.fetchone()
                if row and row.processed_cvs >= row.total_cvs:
                    await session.execute(
                        text("UPDATE batches SET status = 'completed', completed_at = NOW() WHERE id = :id AND status != 'completed'"),
                        {"id": batch_id}
                    )
        logger.info(f"Marked candidate {candidate_id} as failed: {error_msg[:100]}")
    except Exception as e:
        logger.error(f"Failed to mark candidate {candidate_id} as failed: {e}")


async def _async_process_single_cv(candidate_id: str, batch_id: str, r2_key: str, file_type: str, job_id: str, org_id: str, request_id: str):
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
    Process an entire CV batch by fanning out process_single_cv tasks.
    """
    logger.info(f"Processing batch {batch_id}")
    try:
        run_async(_async_process_batch(batch_id))
    except Exception as e:
        logger.error(f"Failed to process batch {batch_id}: {e}")
        try:
            run_async(_mark_batch_failed(batch_id, str(e)))
        except Exception as mark_err:
            logger.error(f"Failed even to mark batch as failed: {mark_err}")


async def _mark_batch_failed(batch_id: str, error_msg: str):
    session_factory = _get_worker_session()
    try:
        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    text("UPDATE batches SET status = 'failed' WHERE id = :id AND status NOT IN ('completed', 'failed')"),
                    {"id": batch_id}
                )
    except Exception as e:
        logger.error(f"Failed to mark batch {batch_id} as failed: {e}")


async def _async_process_batch(batch_id: str):
    session_factory = _get_worker_session()
    async with session_factory() as session:
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
