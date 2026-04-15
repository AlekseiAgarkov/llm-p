from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    prompt: str
    system: Optional[str] = None
    max_history: int = Field(10, ge=0, le=50)
    temperature: float = Field(0.7, ge=0.0, le=2.0)

    model_config = ConfigDict(frozen=True)


class ChatResponse(BaseModel):
    answer: str = Field(..., alias="content")

    model_config = ConfigDict(frozen=True)
