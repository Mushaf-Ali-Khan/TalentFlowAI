from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class BaseResponse(BaseModel):
    success: bool
    request_id: str

class SuccessResponse(BaseResponse, Generic[T]):
    success: bool = True
    data: T
    meta: Optional[dict] = None

class ErrorResponse(BaseResponse):
    success: bool = False
    error: ErrorDetail

class PaginatedMeta(BaseModel):
    page: int
    per_page: int
    total: int

class PaginatedResponse(SuccessResponse[List[T]]):
    meta: PaginatedMeta
