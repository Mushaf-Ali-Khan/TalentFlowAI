from app.repositories.base import BaseRepository
from app.models.job import Job
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

class JobRepository(BaseRepository[Job]):
    def __init__(self):
        super().__init__(Job)
        
    async def get_by_org(self, db: AsyncSession, org_id: str, skip: int = 0, limit: int = 100) -> List[Job]:
        query = select(Job).where(Job.org_id == org_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

job_repo = JobRepository()
