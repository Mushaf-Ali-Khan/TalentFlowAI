from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.batch_repo import batch_repo
from app.models.batch import Batch
from app.workers.cv_tasks import process_cv_batch
import logging

logger = logging.getLogger(__name__)

class PipelineService:
    async def submit_batch(self, db: AsyncSession, org_id: str, job_id: str, user_id: str, r2_keys: list, idempotency_key: str = None) -> Batch:
        if idempotency_key:
            existing_batch = await batch_repo.get_by_idempotency_key(db, idempotency_key)
            if existing_batch:
                logger.info(f"Idempotency hit for key {idempotency_key}")
                return existing_batch

        batch_data = {
            "org_id": org_id,
            "job_id": job_id,
            "submitted_by": user_id,
            "idempotency_key": idempotency_key,
            "status": "queued",
            "total_cvs": len(r2_keys),
            "processed_cvs": 0,
            "failed_cvs": 0
        }
        batch = await batch_repo.create(db, batch_data)
        
        # Here we would also insert Candidate records for each r2_key
        # For simplicity, we assume candidate_repo handles this or we do it inline
        
        # Trigger Celery task
        process_cv_batch.delay(str(batch.id))
        
        return batch

    async def get_batch_status(self, db: AsyncSession, batch_id: str) -> Batch:
        return await batch_repo.get(db, batch_id)

pipeline_service = PipelineService()
