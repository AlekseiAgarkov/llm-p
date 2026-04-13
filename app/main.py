from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_settings
from app.core.config import Settings
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    settings: Settings = get_settings()
    app: FastAPI = FastAPI(title=settings.APP_NAME)

    if settings.ENABLE_CORS:
        app.add_middleware(CORSMiddleware,
                           allow_origins=settings.CORS_ALLOW_ORIGINS,
                           allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
                           allow_methods=settings.CORS_ALLOW_METHODS,
                           allow_headers=settings.CORS_ALLOW_HEADERS)

    @app.get("/health")
    async def health():
        return {"status": "ok", "environment": settings.ENV}

    @app.on_event("startup")
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.on_event("shutdown")
    async def shutdown():
        await engine.dispose()

    return app


# testing tests

app = create_app()
