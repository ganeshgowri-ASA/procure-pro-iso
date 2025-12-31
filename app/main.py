"""Main FastAPI application for Procure-Pro-ISO."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import create_tables
from app.core.exceptions import AppException

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Procure-Pro-ISO application...")
    await create_tables()
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down Procure-Pro-ISO application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Procure-Pro-ISO API

ISO-Compliant Procurement Lifecycle Management System

### Features

- **Vendor Management**: Complete vendor lifecycle management including registration,
  certification tracking, contact management, and performance ratings.

- **RFQ Workflow**: Full Request for Quotation workflow from creation to award,
  including item management, vendor invitations, and quote comparison.

- **Quotation Management**: Vendor quotation submission, evaluation, and acceptance
  with automatic notification system.

- **Email Notifications**: Automated email notifications for RFQ invitations,
  quotation submissions, and status updates.

### ISO Standards Support

- ISO 9001 (Quality Management)
- ISO 14001 (Environmental Management)
- ISO 17025 (Laboratory Competence)
- ISO 45001 (Occupational Health & Safety)
- IATF 16949 (Automotive Quality Management)
- ISO 22000 (Food Safety Management)
- ISO 27001 (Information Security Management)

### API Versioning

All API endpoints are prefixed with `/api/v1/`.
    """,
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Exception Handlers ====================


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application-specific exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "status_code": exc.status_code,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "status_code": 500,
            }
        },
    )


# ==================== Health Check Endpoints ====================


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the application is running.",
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": __version__,
    }


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    description="Welcome message and API information.",
)
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": settings.API_V1_PREFIX,
    }


# ==================== Include API Routes ====================

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ==================== Run Application ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
