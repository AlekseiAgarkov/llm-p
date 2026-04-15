from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from app.api.deps import get_settings, get_engine
from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.core.config import Settings
from app.db import models  # noqa: F401
from app.db.base import Base


def create_app() -> FastAPI:
    settings: Settings = get_settings()
    engine: AsyncEngine = get_engine()
    app: FastAPI = FastAPI(title=settings.APP_NAME)

    if settings.ENABLE_CORS:
        app.add_middleware(CORSMiddleware,
                           allow_origins=settings.CORS_ALLOW_ORIGINS,
                           allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
                           allow_methods=settings.CORS_ALLOW_METHODS,
                           allow_headers=settings.CORS_ALLOW_HEADERS)

    @app.on_event("startup")
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.on_event("shutdown")
    async def shutdown():
        await engine.dispose()

    @app.get("/health")
    async def health():
        return {"status": "ok", "environment": settings.ENV}

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(chat_router, prefix="/chat", tags=["chat"])

    return app


app = create_app()
