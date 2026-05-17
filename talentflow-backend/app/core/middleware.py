import uuid
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # Set request_id in state so it can be accessed by route handlers
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add Request ID to response
            response.headers["X-Request-ID"] = request_id
            
            process_time = time.time() - start_time
            logger.info(
                f"req_id={request_id} method={request.method} path={request.url.path} "
                f"status={response.status_code} duration={process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"req_id={request_id} method={request.method} path={request.url.path} "
                f"error={str(e)} duration={process_time:.3f}s"
            )
            raise
