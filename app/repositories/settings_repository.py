"""App settings repository for database operations."""

from typing import Optional, List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_settings import AppSettings


class SettingsRepository:
    """Repository for AppSettings model database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[AppSettings]:
        """Get all settings."""
        result = await self.db.execute(
            select(AppSettings).order_by(AppSettings.key.asc())
        )
        return list(result.scalars().all())

    async def get_by_key(self, key: str) -> Optional[AppSettings]:
        """Get a setting by key."""
        result = await self.db.execute(
            select(AppSettings).where(AppSettings.key == key)
        )
        return result.scalar_one_or_none()

    async def get_as_dict(self) -> Dict[str, str]:
        """Get all settings as a dictionary."""
        settings = await self.get_all()
        return {s.key: s.value or "" for s in settings}

    async def upsert(self, key: str, value: str, description: Optional[str] = None) -> AppSettings:
        """Create or update a setting."""
        setting = await self.get_by_key(key)
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = AppSettings(key=key, value=value, description=description)
            self.db.add(setting)
        await self.db.flush()
        await self.db.refresh(setting)
        return setting

    async def bulk_upsert(self, settings_dict: Dict[str, str]) -> List[AppSettings]:
        """Bulk create or update settings."""
        results = []
        for key, value in settings_dict.items():
            setting = await self.upsert(key, value)
            results.append(setting)
        return results
