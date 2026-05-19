from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.common import SuccessResponse
from app.schemas.pipeline import UploadUrlRequest, UploadUrlResponseItem, BatchSubmitRequest, BatchStatusResponse
from app.services.pipeline_service import pipeline_service
from app.services.user_service import user_service
from app.core.auth import get_current_user, ClerkUser
from app.core.rbac import require_recruiter
from app.utils.storage import generate_presigned_upload_url
from app.core.database import get_db

router = APIRouter()

@router.post("/upload-urls", response_model=SuccessResponse[List[UploadUrlResponseItem]])
async def get_upload_urls(
    request: Request,
    files: List[UploadUrlRequest],
    current_user: ClerkUser = Depends(require_recruiter)
):
    urls = []
    for f in files:
        urls.append(await generate_presigned_upload_url(f.filename, f.content_type, f.size_bytes))
    return {"success": True, "data": urls, "request_id": request.state.request_id}

@router.post("/submit", response_model=SuccessResponse[BatchStatusResponse])
async def submit_batch(
    request: Request,
    batch_req: BatchSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(require_recruiter)
):
    files = []
    if batch_req.files:
        files = [f.model_dump() for f in batch_req.files]
    elif batch_req.r2_keys:
        files = [
            {
                "r2_key": key,
                "filename": key,
                "size_bytes": 0,
                "content_type": "application/octet-stream",
            }
            for key in batch_req.r2_keys
        ]

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    db_user = await user_service.get_or_create(db, current_user)
    batch = await pipeline_service.submit_batch(
        db=db,
        org_id=str(current_user.org_id),
        job_id=str(batch_req.job_id),
        user_id=str(db_user.id),
        files=files,
        idempotency_key=batch_req.idempotency_key
    )
    return {"success": True, "data": batch, "request_id": request.state.request_id}

@router.get("/{batch_id}", response_model=SuccessResponse[BatchStatusResponse])
async def get_batch_status(
    request: Request,
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_user)
):
    batch = await pipeline_service.get_batch_status(db, batch_id)
    return {"success": True, "data": batch, "request_id": request.state.request_id}
