from typing import List

from fastapi import APIRouter, HTTPException, status

from app.api.deps import ChatUseCaseDep, CurrentUserId
from app.core.errors import ExternalServiceError
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: CurrentUserId, chat_usecase: ChatUseCaseDep):
    try:
        answer = await chat_usecase.ask(
            user_id=user_id,
            prompt=request.prompt,
            system=request.system,
            max_history=request.max_history,
        )
        return ChatResponse(answer=answer)
    except ExternalServiceError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY)


@router.get("/history", response_model=List[ChatResponse])
async def get_history(user_id: CurrentUserId, chat_usecase: ChatUseCaseDep):
    return await chat_usecase.get_history(user_id)


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(user_id: CurrentUserId, chat_usecase: ChatUseCaseDep):
    await chat_usecase.clear_history(user_id)
