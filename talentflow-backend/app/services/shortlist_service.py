from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.shortlist_repo import shortlist_repo
from app.repositories.candidate_repo import candidate_repo
from app.models.candidate import Candidate
from typing import List

class ShortlistService:
    async def get_shortlist_for_batch(self, db: AsyncSession, batch_id: str) -> List[Candidate]:
        # For prototype, just return candidates ordered by score
        # In a real app, we'd query the Shortlist table or rank them
        candidates = await candidate_repo.get_by_batch(db, batch_id)
        # Filter out auto-rejected and sort
        valid_candidates = [c for c in candidates if not c.auto_rejected]
        valid_candidates.sort(key=lambda c: c.total_score or 0, reverse=True)
        return valid_candidates

shortlist_service = ShortlistService()
