import io
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, ClerkUser
from app.core.database import get_db
from app.services.report_service import report_service

router = APIRouter()

@router.get("/batch/{batch_id}")
async def download_batch_report(
    batch_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user),
    format: str = "csv",
):
    format = format.lower()
    if format not in {"csv", "pdf"}:
        raise HTTPException(status_code=400, detail="Unsupported report format")

    if format == "pdf":
        report_bytes = await report_service.generate_batch_report_pdf(db, batch_id)
        filename = f"batch_{batch_id}_report.pdf"
        media_type = "application/pdf"
    else:
        report_bytes = await report_service.generate_batch_report(db, batch_id)
        filename = f"batch_{batch_id}_report.csv"
        media_type = "text/csv"
    return StreamingResponse(
        io.BytesIO(report_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
