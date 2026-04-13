from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User

__all__ = ["UserRepository"]


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, email: str, password_hash: str) -> User:
        user: User = User(email=email, password_hash=password_hash)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def get_by_id(self, user_id: Union[str, UUID]) -> Optional[User]:
        user_id = user_id if isinstance(user_id, UUID) else UUID(user_id)
        result: Result[tuple[User]] = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result: Result[tuple[User]] = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
