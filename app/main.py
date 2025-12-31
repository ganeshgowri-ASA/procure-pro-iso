"""
Procure-Pro-ISO FastAPI Application
ISO-compliant Procurement Lifecycle Management System
"""

from datetime import datetime
from typing import Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db, check_database_connection

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="ISO-compliant Procurement Lifecycle Management System - From RFQ to Asset Management",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "ISO-compliant Procurement Lifecycle Management System",
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    Returns overall system health status.
    """
    db_health = check_database_connection()

    overall_status = "healthy" if db_health["connected"] else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "checks": {
            "database": db_health,
        },
    }


@app.get("/health/db", tags=["Health"])
async def database_health_check() -> dict[str, Any]:
    """
    Database health check endpoint.
    Returns detailed database connectivity status.
    """
    health = check_database_connection()

    if not health["connected"]:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": health.get("error", "Database connection failed"),
            },
        )

    return health


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> dict[str, Any]:
    """
    Kubernetes-style readiness probe.
    Returns 200 if the service is ready to accept traffic.
    """
    db_health = check_database_connection()

    if not db_health["connected"]:
        raise HTTPException(
            status_code=503,
            detail={"ready": False, "reason": "Database not available"},
        )

    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/live", tags=["Health"])
async def liveness_check() -> dict[str, Any]:
    """
    Kubernetes-style liveness probe.
    Returns 200 if the service is alive.
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/v1/db/tables", tags=["Database"])
async def list_tables(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    List all database tables.
    Useful for verifying schema migration.
    """
    from sqlalchemy import text

    result = db.execute(
        text("""
            SELECT table_name,
                   (SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_name = t.table_name AND table_schema = 'public') as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
    )

    tables = [{"name": row[0], "columns": row[1]} for row in result.fetchall()]

    return {
        "count": len(tables),
        "tables": tables,
    }


@app.get("/api/v1/db/schema-version", tags=["Database"])
async def get_schema_version(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Get current database schema version.
    """
    from sqlalchemy import text

    try:
        result = db.execute(
            text("SELECT version, description, applied_at, applied_by FROM schema_version ORDER BY id DESC LIMIT 5")
        )
        versions = [
            {
                "version": row[0],
                "description": row[1],
                "applied_at": row[2].isoformat() if row[2] else None,
                "applied_by": row[3],
            }
            for row in result.fetchall()
        ]

        return {
            "current": versions[0] if versions else None,
            "history": versions,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"Could not retrieve schema version: {str(e)}"},
        )


@app.get("/api/v1/stats", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Get database statistics for key entities.
    """
    from sqlalchemy import text

    stats = {}
    tables = [
        "organizations",
        "users",
        "vendors",
        "categories",
        "products",
        "rfqs",
        "purchase_orders",
        "assets",
    ]

    for table in tables:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            stats[table] = result.fetchone()[0]
        except:
            stats[table] = 0

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "counts": stats,
    }


# Include routers here when you add more API modules
# from app.routers import vendors, rfqs, purchase_orders, assets
# app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["Vendors"])
# app.include_router(rfqs.router, prefix="/api/v1/rfqs", tags=["RFQs"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
