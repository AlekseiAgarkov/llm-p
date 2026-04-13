from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel, ConfigDict


@dataclass
class UserPublic(BaseModel):
    id: UUID
    email: str
    role: str

    model_config = ConfigDict(frozen=True, from_attributes=True)
