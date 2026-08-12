import json
import hashlib
import logging
from typing import Optional
from fastapi import Request, Depends, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from app.config import settings
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

class ClerkUser(BaseModel):
    clerk_user_id: str
    org_id: UUID
    role: str
    email: Optional[str] = None
    full_name: Optional[str] = None

def _extract_email(claims: dict) -> Optional[str]:
    for key in ("email", "email_address", "primary_email_address"):
        value = claims.get(key)
        if isinstance(value, str) and value:
            return value
    emails = claims.get("email_addresses") or claims.get("emailAddresses")
    if isinstance(emails, list) and emails:
        first = emails[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            return first.get("email_address") or first.get("email")
    return None

def _extract_full_name(claims: dict) -> Optional[str]:
    for key in ("full_name", "fullName", "name"):
        value = claims.get(key)
        if isinstance(value, str) and value:
            return value
    first = claims.get("first_name") or claims.get("firstName")
    last = claims.get("last_name") or claims.get("lastName")
    if first or last:
        return f"{first or ''} {last or ''}".strip() or None
    return None

async def verify_clerk_jwt(token: str, redis) -> ClerkUser:
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
        
    cache_key = f"jwt:{hashlib.sha256(token.encode()).hexdigest()[:16]}"
    cached = await redis.get(cache_key)
    if cached:
        return ClerkUser(**json.loads(cached))
        
    # Verify with Clerk SDK
    try:
        claims = None

        try:
            from clerk_backend_api import Clerk
            clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
            if hasattr(clerk, "verify_token"):
                claims = clerk.verify_token(token)
            elif hasattr(clerk, "jwt") and hasattr(clerk.jwt, "verify_token"):
                claims = clerk.jwt.verify_token(token)
        except Exception as e:
            logger.warning(f"Clerk client verify failed: {e}")

        if claims is None:
            try:
                from clerk_backend_api.jwks_helpers import verify_token, VerifyTokenOptions
                claims = verify_token(token, VerifyTokenOptions(secret_key=settings.CLERK_SECRET_KEY))
            except Exception as e:
                logger.warning(f"Clerk verify_token fallback failed: {e}")

        if claims is None:
            raise ValueError("Token verification failed")

        org_id = claims.get("org_id") or claims.get("orgId")
        org_role = claims.get("org_role") or claims.get("orgRole") or "admin"
        email = _extract_email(claims)
        full_name = _extract_full_name(claims)
        
        user = ClerkUser(
            clerk_user_id=claims["sub"],
            org_id=UUID(org_id) if org_id else UUID("00000000-0000-0000-0000-000000000000"),
            role=org_role,
            email=email,
            full_name=full_name,
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
                role="admin",
                email="dev_user@local.test",
                full_name="Dev User"
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
                role="admin",
                email="dev_user@local.test",
                full_name="Dev User"
            )
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
    token = auth_header.split(" ")[1]
    return await verify_clerk_jwt(token, redis)
