from app.repositories.base import BaseRepository
from app.models.batch import Batch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BatchRepository(BaseRepository[Batch]):
    def __init__(self):
        super().__init__(Batch)
        
    async def get_by_idempotency_key(self, db: AsyncSession, key: str) -> Batch:
        query = select(Batch).where(Batch.idempotency_key == key)
        result = await db.execute(query)
        return result.scalar_one_or_none()

batch_repo = BatchRepository()
