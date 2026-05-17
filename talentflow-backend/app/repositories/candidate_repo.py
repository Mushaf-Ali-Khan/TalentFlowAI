from app.repositories.base import BaseRepository
from app.models.candidate import Candidate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self):
        super().__init__(Candidate)
        
    async def get_by_batch(self, db: AsyncSession, batch_id: str) -> List[Candidate]:
        query = select(Candidate).where(Candidate.batch_id == batch_id)
        result = await db.execute(query)
        return list(result.scalars().all())

candidate_repo = CandidateRepository()
