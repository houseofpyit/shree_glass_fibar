"""Device token endpoints for push notifications."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.services.notification_service import NotificationService
from app.models.user import User
from app.schemas.device_token import DeviceTokenCreate
from app.schemas.common import StandardResponse
from app.core.response import success_response

router = APIRouter()


@router.post(
    "",
    response_model=StandardResponse,
    summary="Register device token",
    description="Register or update Firebase FCM device token for push notifications.",
)
async def register_device_token(
    data: DeviceTokenCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register or update device token for push notifications."""
    notification_service = NotificationService(db)
    await notification_service.register_device(
        user_id=current_user.id,
        token=data.token,
        platform=data.platform,
    )
    return success_response(message="Device token registered successfully")
