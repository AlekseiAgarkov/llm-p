from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from app.core.config import settings

__all__ = ["engine", "AsyncSessionLocal"]

DATABASE_URL = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal: async_sessionmaker[AsyncSession | Any] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)
