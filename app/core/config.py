from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["settings"]


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

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8"
    )


settings = Settings()
