"""Application settings and configuration management."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = "Procure-Pro-ISO"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Database settings - Railway PostgreSQL
    database_url: str = "postgresql://postgres:XHKYkvrniDAQepUbKlTadhtiMqExKxBf@postgres.railway.internal:5432/railway"
    database_echo: bool = False

    @field_validator("database_url", mode="after")
    @classmethod
    def convert_to_async_url(cls, v: str) -> str:
        """Convert database URL to async format for SQLAlchemy."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for migrations."""
        url = self.database_url
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "")
        return url

    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # TBE Scoring defaults
    default_price_weight: float = 0.40
    default_quality_weight: float = 0.25
    default_delivery_weight: float = 0.20
    default_compliance_weight: float = 0.15

    # Report settings
    report_output_dir: str = "./reports"
    chart_dpi: int = 150


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
