"""Application settings and configuration management."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Database settings
    database_url: str = "sqlite+aiosqlite:///./procure_pro.db"
    database_echo: bool = False

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
