from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.repositories.users import UserRepository


def get_settings() -> Settings:
    return settings


def get_user_repository(session: AsyncSession):
    return UserRepository(session)
