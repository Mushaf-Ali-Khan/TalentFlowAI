from fastapi import Request, status
from fastapi.responses import JSONResponse

class TalentFlowException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

async def talentflow_exception_handler(request: Request, exc: TalentFlowException):
    request_id = getattr(request.state, "request_id", None)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            },
            "request_id": request_id
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred."
            },
            "request_id": request_id
        }
    )
