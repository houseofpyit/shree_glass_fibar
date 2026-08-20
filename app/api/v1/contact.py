"""Contact information endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.contact_service import ContactService
from app.repositories.audit_repository import AuditRepository
from app.repositories.settings_repository import SettingsRepository
from app.schemas.contact import ContactInfoUpdate, ContactInfoResponse
from app.schemas.common import StandardResponse
from app.core.response import success_response

router = APIRouter()


@router.get(
    "",
    response_model=StandardResponse,
    summary="Get contact information",
    description="Get company contact information along with social media links from settings.",
)
async def get_contact(db: AsyncSession = Depends(get_db)):
    """Get contact information with social links."""
    contact_service = ContactService(db)
    contact = await contact_service.get_contact_info()
    contact_data = ContactInfoResponse.model_validate(contact).model_dump()

    # Add social media links from settings
    settings_repo = SettingsRepository(db)
    settings_dict = await settings_repo.get_as_dict()
    social_links = {
        "youtube_url": settings_dict.get("youtube_url", ""),
        "instagram_url": settings_dict.get("instagram_url", ""),
        "facebook_url": settings_dict.get("facebook_url", ""),
    }
    contact_data["social_links"] = social_links

    return success_response(data=contact_data, message="Contact information retrieved")


@router.put(
    "/admin",
    response_model=StandardResponse,
    summary="Update contact information (admin)",
    description="Update company contact information. Admin only.",
)
async def update_contact(
    data: ContactInfoUpdate,
    request: Request,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update contact information (admin)."""
    contact_service = ContactService(db)
    contact = await contact_service.update_contact_info(data)

    audit_repo = AuditRepository(db)
    await audit_repo.create(
        actor_email=admin["email"],
        action="update_contact",
        resource_type="contact_information",
        ip_address=request.client.host if request.client else None,
    )

    contact_data = ContactInfoResponse.model_validate(contact).model_dump()
    return success_response(data=contact_data, message="Contact information updated")
