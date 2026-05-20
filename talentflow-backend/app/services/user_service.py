import logging
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.core.auth import ClerkUser
from app.repositories.user_repo import user_repo
from app.models.user import User

logger = logging.getLogger(__name__)


class UserService:
    async def get_or_create(self, db: AsyncSession, clerk_user: ClerkUser) -> User:
        existing = await user_repo.get_by_clerk_id(db, clerk_user.clerk_user_id)
        if existing:
            return existing

        email = clerk_user.email
        if not email:
            if settings.ENVIRONMENT == "development":
                email = f"{clerk_user.clerk_user_id}@local.test"
            else:
                raise HTTPException(status_code=400, detail="Email missing from token")

        user_data = {
            "org_id": clerk_user.org_id,
            "clerk_user_id": clerk_user.clerk_user_id,
            "email": email,
            "full_name": clerk_user.full_name,
            "role": clerk_user.role,
        }
        logger.info(f"Creating user record for Clerk ID {clerk_user.clerk_user_id}")
        return await user_repo.create(db, user_data)


user_service = UserService()
