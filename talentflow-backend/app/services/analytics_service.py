from sqlalchemy import select, func
from app.models.candidate import Candidate
from app.models.job import Job

class AnalyticsService:
    async def get_overview(self, db, org_id):
        total_candidates = await db.execute(
            select(func.count(Candidate.id)).where(Candidate.org_id == org_id)
        )
        total_candidates = total_candidates.scalar() or 0

        avg_total_score = await db.execute(
            select(func.avg(Candidate.total_score)).where(Candidate.org_id == org_id)
        )
        avg_total_score = float(avg_total_score.scalar() or 0.0)

        avg_semantic_score = await db.execute(
            select(func.avg(Candidate.semantic_score)).where(Candidate.org_id == org_id)
        )
        avg_semantic_score = float(avg_semantic_score.scalar() or 0.0)

        passed_candidates = await db.execute(
            select(func.count(Candidate.id)).where(
                Candidate.org_id == org_id,
                Candidate.auto_rejected.is_(False),
                Candidate.total_score >= 70
            )
        )
        passed_candidates = passed_candidates.scalar() or 0

        active_jobs = await db.execute(
            select(func.count(Job.id)).where(Job.org_id == org_id)
        )
        active_jobs = active_jobs.scalar() or 0

        pass_rate = (passed_candidates / total_candidates) if total_candidates else 0.0

        score_rows = await db.execute(
            select(Candidate.total_score).where(Candidate.org_id == org_id)
        )
        distribution = {
            "0-49": 0,
            "50-59": 0,
            "60-69": 0,
            "70-79": 0,
            "80-89": 0,
            "90-100": 0,
        }
        for (score,) in score_rows.fetchall():
            if score is None:
                continue
            if score < 50:
                distribution["0-49"] += 1
            elif score < 60:
                distribution["50-59"] += 1
            elif score < 70:
                distribution["60-69"] += 1
            elif score < 80:
                distribution["70-79"] += 1
            elif score < 90:
                distribution["80-89"] += 1
            else:
                distribution["90-100"] += 1

        return {
            "total_candidates": total_candidates,
            "avg_total_score": round(avg_total_score, 2),
            "avg_semantic_score": round(avg_semantic_score, 4),
            "pass_rate": round(pass_rate, 4),
            "active_jobs": active_jobs,
            "score_distribution": distribution,
        }

analytics_service = AnalyticsService()
