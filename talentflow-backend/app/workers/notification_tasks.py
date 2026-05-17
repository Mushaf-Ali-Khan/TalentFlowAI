import logging
from app.workers.celery_app import app

logger = logging.getLogger(__name__)

@app.task(bind=True)
def send_batch_complete_email(self, batch_id: str, email_to: str):
    logger.info(f"Sending batch completion email for batch {batch_id} to {email_to}")
    # Placeholder
    pass
