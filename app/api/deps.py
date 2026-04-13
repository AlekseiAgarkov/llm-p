from typing import Annotated, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase


def get_settings() -> Settings:
    return settings


SettingsDep: Type[Settings] = Annotated[Settings, Depends(get_settings)]


def get_user_repository(session: AsyncSession):
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_auth_usecase(user_repository: UserRepositoryDep, settings: SettingsDep) -> AuthUseCase:
    return AuthUseCase(user_repository, settings)
