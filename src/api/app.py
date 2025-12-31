"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.database import init_db, close_db
from src.config.settings import get_settings
from src.api.routes import vendors, tbe, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "ISO-compliant procurement lifecycle management system with "
            "Technical Bid Evaluation (TBE) scoring engine. "
            "Supports vendor comparison, TCO analysis, and compliance scoring."
        ),
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    api_prefix = settings.api_prefix

    app.include_router(
        vendors.router,
        prefix=f"{api_prefix}/vendors",
        tags=["Vendors"],
    )

    app.include_router(
        tbe.router,
        prefix=f"{api_prefix}/tbe",
        tags=["TBE Scoring"],
    )

    app.include_router(
        reports.router,
        prefix=f"{api_prefix}/reports",
        tags=["Reports"],
    )

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "ISO-compliant procurement management with TBE scoring",
            "docs": "/api/docs",
            "api_prefix": api_prefix,
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": settings.app_version}

    return app


# Create application instance
app = create_app()
