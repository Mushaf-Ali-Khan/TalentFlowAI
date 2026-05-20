from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    async def get_by_clerk_id(self, db: AsyncSession, clerk_user_id: str) -> User | None:
        result = await db.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        return result.scalar_one_or_none()


user_repo = UserRepository(User)
