"""Application configuration using environment variables."""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Procure-Pro-ISO"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database - Railway PostgreSQL
    database_url: Optional[str] = None

    # Individual database components (Railway format)
    pghost: Optional[str] = None
    pgport: str = "5432"
    pgdatabase: Optional[str] = None
    pguser: Optional[str] = None
    pgpassword: Optional[str] = None

    # Connection pool settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_database_url(self) -> str:
        """Build database URL from environment variables."""
        # Priority 1: Direct DATABASE_URL
        if self.database_url:
            return self.database_url

        # Priority 2: Build from individual components
        if all([self.pghost, self.pgdatabase, self.pguser, self.pgpassword]):
            return (
                f"postgresql://{self.pguser}:{self.pgpassword}"
                f"@{self.pghost}:{self.pgport}/{self.pgdatabase}"
            )

        # Fallback for local development
        return "postgresql://postgres:postgres@localhost:5432/procure_pro_iso"

    def get_async_database_url(self) -> str:
        """Get async database URL for asyncpg."""
        url = self.get_database_url()
        return url.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
