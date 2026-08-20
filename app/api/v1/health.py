"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.config import settings
from app.core.response import success_response

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Basic health check endpoint. Returns OK if the service is running.",
)
async def health_check():
    """Basic health check."""
    return success_response(
        data={
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
        },
        message="Service is healthy",
    )


@router.get(
    "/ready",
    summary="Readiness check",
    description="Readiness check verifying database connectivity.",
)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check - verifies database connection."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    is_ready = db_status == "connected"
    return {
        "success": is_ready,
        "message": "Service is ready" if is_ready else "Service not ready",
        "data": {
            "database": db_status,
            "maintenance_mode": settings.MAINTENANCE_MODE,
        },
    }
