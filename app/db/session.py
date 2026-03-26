from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

__all__ = ["engine", "AsyncSessionLocal"]

DATABASE_URL = f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)
