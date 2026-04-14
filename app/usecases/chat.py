from typing import List, Optional
from uuid import UUID

from app.repositories.chat_messages import ChatMessageRepository
from app.schemas.chat import ChatResponse
from app.services.openrouter_client import OpenRouterClient, OpenRouterMessage


class ChatUseCase:
    def __init__(
            self,
            chat_repo: ChatMessageRepository,
            openrouter_client: OpenRouterClient,
    ):
        self._chat_repo = chat_repo
        self._openrouter = openrouter_client

    async def ask(self, user_id: UUID, prompt: str, system: Optional[str] = None, max_history: int = 10) -> str:
        messages = []
        if system:
            messages.append(OpenRouterMessage(role="system", content=system))

        history = await self._chat_repo.get_recent(user_id, max_history)
        for msg in history:
            messages.append(OpenRouterMessage(role=msg.role, content=msg.content))

        messages.append(OpenRouterMessage(role="user", content=prompt))

        await self._chat_repo.add(user_id, "user", prompt)

        answer = await self._openrouter.get_model_response(messages)

        await self._chat_repo.add(user_id, "assistant", answer)

        return answer

    async def get_history(self, user_id: UUID, limit: int = 100) -> List[ChatResponse]:
        messages = await self._chat_repo.get_recent(user_id, limit=limit)
        return [ChatResponse.model_validate(msg) for msg in messages]

    async def clear_history(self, user_id: UUID) -> None:
        await self._chat_repo.delete_all_for_user(user_id)
