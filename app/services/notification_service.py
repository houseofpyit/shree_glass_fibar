"""Push notification service (placeholder for Firebase FCM)."""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.device_token_repository import DeviceTokenRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """Placeholder service for push notifications via Firebase FCM."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.token_repo = DeviceTokenRepository(db)

    async def register_device(self, user_id: int, token: str, platform: str):
        """Register or update a device token."""
        return await self.token_repo.upsert(user_id, token, platform)

    async def send_to_user(
        self, user_id: int, title: str, body: str, data: Optional[dict] = None
    ) -> bool:
        """
        Send push notification to a specific user.
        TODO: Implement Firebase FCM integration.
        """
        tokens = await self.token_repo.get_by_user(user_id)
        if not tokens:
            logger.info(f"No device tokens found for user {user_id}")
            return False

        # Placeholder: Log notification instead of sending
        for token in tokens:
            logger.info(
                f"[PLACEHOLDER] Push notification to user {user_id} "
                f"({token.platform}): {title} - {body}"
            )

        return True

    async def send_to_all(
        self, title: str, body: str, data: Optional[dict] = None
    ) -> int:
        """
        Send push notification to all users.
        TODO: Implement batch Firebase FCM sending.
        """
        logger.info(f"[PLACEHOLDER] Broadcast notification: {title} - {body}")
        return 0
