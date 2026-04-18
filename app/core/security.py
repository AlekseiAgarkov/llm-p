from dataclasses import dataclass
from datetime import datetime, UTC
from enum import Enum
from typing import Dict, Any

import bcrypt
from fastapi.security import HTTPBasic
from jose import jwt
from passlib.context import CryptContext

security = HTTPBasic()


@dataclass
class SilenceBcryptWarningBug:
    """
    __about__ в bcrypt сломан для версий после 4.0.1. Описано тут:
        - https://foss.heptapod.net/python-libs/passlib/-/work_items/190
        - https://stackoverflow.com/questions/79469355/error-attributeerror-problem-with-passlibbcrypt-module

    Как чинить предложено тут:
        https://github.com/pyca/bcrypt/issues/684#issuecomment-2430047176

    Добавил, чтобы:
     - bcrypt не ругался на __about__;
     - не downgrade'ить;
     - соблюсти условие задания;
     - можно было ловить ошибки.
    """
    __version__: str = getattr(bcrypt, "__version__")


setattr(bcrypt, "__about__", SilenceBcryptWarningBug())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

__all__ = ["security",
           "hash_password",
           "verify_password",
           "create_access_token",
           "decode_token"]


class JWTTokenType(Enum):
    refresh = "refresh"
    access = "access"


@dataclass(frozen=True)
class JWTAccessToken:
    sub: str
    type: str
    iat: int
    exp: int


@dataclass(frozen=True)
class JWTRefreshToken:
    sub: str
    type: str
    jti: str
    iat: int
    exp: int


def _now() -> int:
    return int(datetime.now(UTC).timestamp())


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(sub: str, jwt_secret: str, jwt_algorithm: str, token_expire_minutes: int) -> str:
    now: int = _now()
    payload: dict = JWTAccessToken(sub=sub,
                                   type=JWTTokenType.access.name,
                                   iat=now,
                                   exp=now + token_expire_minutes).__dict__
    return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)


def is_expired(decoded_payload: Dict[str, Any]) -> bool:
    exp = decoded_payload.get('exp')
    if not exp:
        return False
    return _now() > exp


def decode_token(token: str, jwt_secret: str, jwt_algorithm: str) -> Dict[str, Any]:
    decoded = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])

    if is_expired(decoded):
        raise jwt.ExpiredSignatureError("Token has expired")

    return decoded
