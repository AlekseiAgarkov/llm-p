from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def create_app() -> FastAPI:
    application: FastAPI = FastAPI(title=settings.APP_NAME)

    @application.get("/health")
    async def health():
        return {"status": "ok", "environment": settings.ENV}

    if settings.ENABLE_CORS:
        application.add_middleware(CORSMiddleware,
                                   allow_origins=settings.CORS_ALLOW_ORIGINS,
                                   allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
                                   allow_methods=settings.CORS_ALLOW_METHODS,
                                   allow_headers=settings.CORS_ALLOW_HEADERS)

    return application


app = create_app()
