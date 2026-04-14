from typing import Annotated, Type, Optional, Dict, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from app.core.config import settings, Settings
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal, engine
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
OAuth2PasswordRequestFormDep: Type[OAuth2PasswordRequestForm] = Annotated[OAuth2PasswordRequestForm, Depends()]


def get_engine() -> AsyncEngine:
    return engine


def get_settings() -> Settings:
    return settings


SettingsDep: Type[Settings] = Annotated[Settings, Depends(get_settings)]


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


SessionDep: Type[AsyncSession] = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep: Type[UserRepository] = Annotated[UserRepository, Depends(get_user_repository)]


def get_auth_usecase(user_repository: UserRepositoryDep, settings: SettingsDep) -> AuthUseCase:
    return AuthUseCase(user_repository, settings)


AuthUseCaseDep: Type[AuthUseCase] = Annotated[AuthUseCase, Depends(get_auth_usecase)]


async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)], settings: SettingsDep) -> UUID:
    try:
        payload: Dict[str, Any] = decode_token(token, jwt_secret=settings.JWT_SECRET, jwt_algorithm=settings.JWT_ALG)
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UUID(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUserId: Type[UUID] = Annotated[UUID, Depends(get_current_user_id)]
