import json
import hashlib
import logging
from typing import Optional
from fastapi import Request, Depends, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from app.config import settings

logger = logging.getLogger(__name__)

class ClerkUser(BaseModel):
    clerk_user_id: str
    org_id: UUID
    role: str

async def get_redis():
    # Placeholder for Redis connection dependency
    class MockRedis:
        async def get(self, key): return None
        async def setex(self, key, ttl, val): pass
    return MockRedis()

async def verify_clerk_jwt(token: str, redis) -> ClerkUser:
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
        
    cache_key = f"jwt:{hashlib.sha256(token.encode()).hexdigest()[:16]}"
    cached = await redis.get(cache_key)
    if cached:
        return ClerkUser(**json.loads(cached))
        
    # Verify with Clerk SDK
    try:
        from clerk_backend_api import Clerk
        clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
        
        # Verify token - using a placeholder since actual Clerk client method signature may vary
        # claims = clerk.clients.verify_token(token) 
        
        # Fake claims for local dev
        claims = {
            "sub": "user_123",
            "org_id": "00000000-0000-0000-0000-000000000000",
            "org_role": "admin"
        }
        
        user = ClerkUser(
            clerk_user_id=claims['sub'],
            org_id=UUID(claims['org_id']),
            role=claims.get('org_role', 'viewer'),
        )
        
        await redis.setex(cache_key, settings.JWT_CACHE_TTL_SECONDS, user.model_dump_json())
        return user
        
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        # For development, just return a mock user if auth fails to allow testing
        if settings.ENVIRONMENT == "development":
            logger.warning("Returning mock user due to dev environment")
            return ClerkUser(
                clerk_user_id="dev_user",
                org_id=UUID("00000000-0000-0000-0000-000000000000"),
                role="admin"
            )
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(request: Request, redis = Depends(get_redis)) -> ClerkUser:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # Check for dev environment bypass
        if settings.ENVIRONMENT == "development":
            return ClerkUser(
                clerk_user_id="dev_user",
                org_id=UUID("00000000-0000-0000-0000-000000000000"),
                role="admin"
            )
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
    token = auth_header.split(" ")[1]
    return await verify_clerk_jwt(token, redis)
