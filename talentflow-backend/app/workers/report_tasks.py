import logging
from app.workers.celery_app import app
from app.services.report_service import report_service
from app.core.database import async_session

logger = logging.getLogger(__name__)

@app.task(bind=True)
def generate_batch_report(self, batch_id: str):
    logger.info(f"Generating report for batch {batch_id}")
    async def _run():
        async with async_session() as session:
            await report_service.generate_batch_report(session, batch_id)

    import asyncio
    asyncio.run(_run())
