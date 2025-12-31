"""
Configuration management for Procure-Pro-ISO.

Uses pydantic-settings to load configuration from environment variables.
"""

import os
from functools import lru_cache
from typing import Any

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database Configuration
    database_url: str = "postgresql://postgres:XHKYkvrniDAQepUbKlTadhtiMqExKxBf@postgres.railway.internal:5432/railway"

    # Database Pool Settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # Application Settings
    app_name: str = "Procure-Pro-ISO"
    app_version: str = "0.1.0"
    debug: bool = False

    # Parser Settings
    enable_ocr: bool = True
    ocr_language: str = "eng"
    ocr_dpi: int = 300
    multi_vendor_mode: bool = True
    strict_validation: bool = False

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate and potentially transform the database URL."""
        if not v:
            raise ValueError("DATABASE_URL must be set")
        # Handle Railway's internal URL format
        if v.startswith("postgresql://") or v.startswith("postgres://"):
            return v
        raise ValueError("Invalid database URL format")

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def async_database_url(self) -> str:
        """Get async database URL for asyncpg."""
        url = self.sync_database_url
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance loaded from environment.
    """
    return Settings()


# Convenience access to settings
settings = get_settings()
