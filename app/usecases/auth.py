from typing import Optional, Union
from uuid import UUID

from app.core.config import Settings
from app.core.errors import NotFoundError, UnauthorizedError, EmailAlreadyRegisteredError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import UserRepository
from app.schemas.user import UserPublic
from app.db.models import User


class AuthUseCase:
    def __init__(self, user_repository: UserRepository, settings: Settings):
        self._user_repository = user_repository
        self._settings = settings

    async def register(self, email: str, password: str) -> UserPublic:
        user_exists: Optional[User] = await self._user_repository.get_by_email(email)
        if user_exists:
            raise EmailAlreadyRegisteredError("Email already registered")

        password_hash: str = hash_password(password)
        user: User = await self._user_repository.create(email, password_hash)
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> str:
        user: Optional[User] = await self._user_repository.get_by_email(email)
        if not user:
            raise UnauthorizedError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        return create_access_token(sub=str(user.id),
                                   jwt_secret=self._settings.JWT_SECRET,
                                   jwt_algorithm=self._settings.JWT_ALG,
                                   token_expire_minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    async def get_profile(self, user_id: Union[str, UUID]) -> UserPublic:
        user_id = user_id if isinstance(user_id, UUID) else UUID(user_id)
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserPublic.model_validate(user)
