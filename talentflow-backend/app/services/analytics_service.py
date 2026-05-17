class AnalyticsService:
    async def get_overview(self, db, org_id):
        return {"total_candidates": 0, "avg_score": 0.0}

analytics_service = AnalyticsService()
