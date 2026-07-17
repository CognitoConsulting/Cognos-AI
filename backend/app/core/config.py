from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Cognos AI"
    app_version: str = "0.1.0"
    environment: str = "local"
    platform_admin_token: str = "local-dev-platform-admin-token"
    auth_token_secret: str = "local-dev-auth-token-secret-change-me"
    auth_token_ttl_seconds: int = 60 * 60 * 24
    daily_summary_scheduler_enabled: bool = True
    daily_summary_scheduler_interval_seconds: int = 60
    database_url: str = Field(
        default="postgresql+psycopg://cognos:cognos@db:5432/cognos_ai"
    )
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

