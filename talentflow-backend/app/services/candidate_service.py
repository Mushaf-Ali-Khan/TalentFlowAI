from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.repositories.candidate_repo import candidate_repo
from app.models.candidate import Candidate

class CandidateService:
    async def get_candidate(self, db: AsyncSession, candidate_id: str) -> Candidate:
        return await candidate_repo.get(db, candidate_id)

    async def update_status(self, db: AsyncSession, candidate_id: str, status: str, note: str, user_id: str) -> Candidate:
        candidate = await candidate_repo.get(db, candidate_id)
        if not candidate:
            return None
            
        update_data = {
            "recruiter_status": status,
            "recruiter_note": note,
            "status_updated_by": user_id,
            "status_updated_at": datetime.now(timezone.utc)
        }
        return await candidate_repo.update(db, candidate, update_data)

candidate_service = CandidateService()
