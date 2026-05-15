from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://pdfintoword:pdfintoword@localhost:5432/pdfintoword"
    redis_url: str = "redis://localhost:6379/0"

    storage_backend: str = "local"
    local_storage_path: str = "./data"

    oci_namespace: str = ""
    oci_bucket_name: str = ""
    oci_region: str = ""
    oci_config_file: str = ""

    max_upload_mb: int = 25
    max_pdf_pages: int = 100
    job_ttl_hours: int = 24
    celery_concurrency: int = 2

    rate_limit_per_minute: int = 10

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
