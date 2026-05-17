from fastapi import APIRouter
from app.schemas.common import SuccessResponse

router = APIRouter()

@router.get("", response_model=SuccessResponse[dict])
async def check_health():
    return {"success": True, "data": {"status": "ok"}, "request_id": ""}
