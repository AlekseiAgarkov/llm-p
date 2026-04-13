from fastapi import FastAPI

from app.core.config import settings


def create_app() -> FastAPI:
    application: FastAPI = FastAPI(title=settings.APP_NAME)

    @application.get("/health")
    async def health():
        return {"status": "ok", "environment": settings.ENV}

    return application


app = create_app()
