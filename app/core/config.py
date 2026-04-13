from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["settings", "Settings"]


class Settings(BaseSettings):
    APP_NAME: str
    ENV: str
    JWT_SECRET: str
    JWT_ALG: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SQLITE_PATH: Path
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = Field(..., json_schema_extra={"format": "url"})
    OPENROUTER_MODEL: str
    OPENROUTER_SITE_URL: str = Field(..., json_schema_extra={"format": "url"})
    OPENROUTER_APP_NAME: str

    ENABLE_CORS: bool = Field(default=False)
    CORS_ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: List[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
