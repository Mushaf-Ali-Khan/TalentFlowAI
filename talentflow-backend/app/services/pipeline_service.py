from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.batch_repo import batch_repo
from app.repositories.candidate_repo import candidate_repo
from app.models.batch import Batch
from app.workers.cv_tasks import process_cv_batch
import hashlib
import logging

logger = logging.getLogger(__name__)

class PipelineService:
    async def submit_batch(self, db: AsyncSession, org_id: str, job_id: str, user_id: str, files: list, idempotency_key: str = None) -> Batch:
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
            "total_cvs": len(files),
            "processed_cvs": 0,
            "failed_cvs": 0
        }
        batch = await batch_repo.create(db, batch_data)

        for item in files:
            r2_key = item.get("r2_key")
            filename = item.get("filename") or r2_key
            size_bytes = int(item.get("size_bytes") or 0)

            hash_input = f"{r2_key}|{filename}|{size_bytes}".encode("utf-8")
            content_hash = hashlib.sha256(hash_input).hexdigest()

            candidate_data = {
                "org_id": org_id,
                "job_id": job_id,
                "batch_id": batch.id,
                "r2_key": r2_key,
                "original_filename": filename,
                "file_size_bytes": size_bytes,
                "content_hash": content_hash,
                "processing_status": "pending",
            }
            await candidate_repo.create(db, candidate_data)

        await db.commit()

        # Trigger Celery task after data is persisted
        process_cv_batch.delay(str(batch.id))
        
        return batch

    async def get_batch_status(self, db: AsyncSession, batch_id: str) -> Batch:
        return await batch_repo.get(db, batch_id)

pipeline_service = PipelineService()
