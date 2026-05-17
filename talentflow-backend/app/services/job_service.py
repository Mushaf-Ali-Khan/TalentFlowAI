from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.job_repo import job_repo
from app.models.job import Job
from typing import List

class JobService:
    async def create_job(self, db: AsyncSession, job_data: dict, org_id: str, user_id: str) -> Job:
        job_data['org_id'] = org_id
        job_data['created_by'] = user_id
        return await job_repo.create(db, job_data)

    async def get_jobs_for_org(self, db: AsyncSession, org_id: str, skip: int = 0, limit: int = 100) -> List[Job]:
        return await job_repo.get_by_org(db, org_id, skip, limit)

    async def get_job(self, db: AsyncSession, job_id: str) -> Job:
        return await job_repo.get(db, job_id)

job_service = JobService()
