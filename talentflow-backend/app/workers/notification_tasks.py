import logging
import smtplib
from email.message import EmailMessage
from app.config import settings
from app.workers.celery_app import app

logger = logging.getLogger(__name__)

@app.task(bind=True)
def send_batch_complete_email(self, batch_id: str, email_to: str):
    logger.info(f"Sending batch completion email for batch {batch_id} to {email_to}")
    if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
        logger.warning("SMTP is not configured; skipping batch completion email")
        return

    message = EmailMessage()
    message["Subject"] = f"TalentFlow AI: Batch {batch_id} completed"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = email_to
    message.set_content(
        "\n".join([
            "Your CV batch has finished processing.",
            f"Batch ID: {batch_id}",
            "You can review the shortlist in the TalentFlow AI dashboard.",
        ])
    )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
            server.send_message(message)
        logger.info(f"Batch completion email sent for {batch_id}")
    except Exception as e:
        logger.error(f"Failed to send batch completion email: {e}")
        raise
