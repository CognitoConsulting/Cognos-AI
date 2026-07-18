from functools import lru_cache

from pydantic import Field, SecretStr
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
    voice_transcription_enabled: bool = False
    voice_transcription_provider: str = "not_configured"
    openai_api_key: SecretStr | None = None
    openai_transcription_model: str = "gpt-4o-mini-transcribe"
    voice_transcription_max_bytes: int = 25 * 1024 * 1024
    voice_transcription_download_timeout_seconds: int = 20
    meta_whatsapp_access_token: SecretStr | None = None
    meta_graph_api_version: str = "v23.0"
    whatsapp_media_download_timeout_seconds: int = 20
    media_storage_provider: str = "local_filesystem"
    media_storage_local_root: str = "media"
    media_storage_max_bytes: int = 100 * 1024 * 1024
    media_storage_download_timeout_seconds: int = 30
    media_storage_s3_bucket: str | None = None
    media_storage_s3_region: str | None = None
    media_storage_s3_endpoint_url: str | None = None
    media_storage_s3_public_base_url: str | None = None
    media_storage_s3_prefix: str = ""
    media_storage_s3_access_key_id: SecretStr | None = None
    media_storage_s3_secret_access_key: SecretStr | None = None
    media_storage_s3_presigned_url_ttl_seconds: int = 600
    database_url: str = Field(
        default="postgresql+psycopg://cognos:cognos@db:5432/cognos_ai"
    )
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

