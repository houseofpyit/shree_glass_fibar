"""Device token repository for database operations."""

from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device_token import DeviceToken


class DeviceTokenRepository:
    """Repository for DeviceToken model database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(self, user_id: int, token: str, platform: str) -> DeviceToken:
        """Create or update device token for a user."""
        result = await self.db.execute(
            select(DeviceToken).where(
                DeviceToken.user_id == user_id,
                DeviceToken.platform == platform,
            )
        )
        device_token = result.scalar_one_or_none()

        if device_token:
            device_token.token = token
        else:
            device_token = DeviceToken(user_id=user_id, token=token, platform=platform)
            self.db.add(device_token)

        await self.db.flush()
        await self.db.refresh(device_token)
        return device_token

    async def get_by_user(self, user_id: int) -> List[DeviceToken]:
        """Get all device tokens for a user."""
        result = await self.db.execute(
            select(DeviceToken).where(DeviceToken.user_id == user_id)
        )
        return list(result.scalars().all())

    async def delete_by_user(self, user_id: int) -> None:
        """Delete all device tokens for a user."""
        await self.db.execute(
            delete(DeviceToken).where(DeviceToken.user_id == user_id)
        )
        await self.db.flush()
