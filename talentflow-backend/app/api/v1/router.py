from fastapi import APIRouter
from .health import router as health_router
from .jobs import router as jobs_router
from .pipeline import router as pipeline_router
from .candidates import router as candidates_router
from .shortlists import router as shortlists_router
from .analytics import router as analytics_router
from .reports import router as reports_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["pipeline"])
api_router.include_router(candidates_router, prefix="/candidates", tags=["candidates"])
api_router.include_router(shortlists_router, prefix="/shortlists", tags=["shortlists"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])

