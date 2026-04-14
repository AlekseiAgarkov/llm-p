from typing import List
from uuid import UUID

from sqlalchemy import delete, select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage


class ChatMessageRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, user_id: UUID, role: str, content: str) -> ChatMessage:
        message = ChatMessage(user_id=user_id, role=role, content=content)
        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)
        return message

    async def get_recent(self, user_id: UUID, limit: int) -> List[ChatMessage]:
        result: Result[tuple[ChatMessage]] = await self._session.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_all_for_user(self, user_id: UUID) -> None:
        await self._session.execute(delete(ChatMessage).where(ChatMessage.user_id == user_id))
        await self._session.commit()
