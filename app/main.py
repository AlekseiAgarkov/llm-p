import uvicorn
from fastapi import FastAPI

from core.config import settings


def create_app() -> FastAPI:
    application: FastAPI = FastAPI(title=settings.APP_NAME)

    @application.get("/health")
    async def health():
        return {"status": "ok", "environment": settings.ENV}

    return application


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
