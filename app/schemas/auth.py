from dataclasses import dataclass

from pydantic import BaseModel, EmailStr, Field, ConfigDict


@dataclass
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=16)

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True, extra="forbid")


@dataclass
class TokenResponse:
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(frozen=True)


@dataclass
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=16)

    model_config = ConfigDict(frozen=True)
