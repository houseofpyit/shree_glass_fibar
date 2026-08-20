"""App settings endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.settings_service import SettingsService
from app.repositories.audit_repository import AuditRepository
from app.schemas.settings import AppSettingsUpdate
from app.schemas.common import StandardResponse
from app.core.response import success_response

router = APIRouter()


@router.get(
    "",
    response_model=StandardResponse,
    summary="Get all settings",
    description="Get all application settings as key-value pairs. Public endpoint for mobile app.",
)
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Get all application settings."""
    settings_service = SettingsService(db)
    settings_dict = await settings_service.get_as_dict()
    return success_response(data=settings_dict, message="Settings retrieved")


@router.put(
    "/admin",
    response_model=StandardResponse,
    summary="Update settings (admin)",
    description="Bulk update application settings. Admin only.",
)
async def update_settings(
    data: AppSettingsUpdate,
    request: Request,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update application settings (admin)."""
    settings_service = SettingsService(db)
    await settings_service.update_settings(data.settings)

    audit_repo = AuditRepository(db)
    await audit_repo.create(
        actor_email=admin["email"],
        action="update_settings",
        resource_type="app_settings",
        details=f"Updated keys: {', '.join(data.settings.keys())}",
        ip_address=request.client.host if request.client else None,
    )

    return success_response(message="Settings updated successfully")
