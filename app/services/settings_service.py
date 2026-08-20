"""App settings service."""

from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_settings import AppSettings
from app.repositories.settings_repository import SettingsRepository


class SettingsService:
    """Service for application settings operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings_repo = SettingsRepository(db)

    async def get_all(self) -> List[AppSettings]:
        """Get all settings."""
        return await self.settings_repo.get_all()

    async def get_as_dict(self) -> Dict[str, str]:
        """Get all settings as a dictionary."""
        return await self.settings_repo.get_as_dict()

    async def update_settings(self, settings_dict: Dict[str, str]) -> List[AppSettings]:
        """Bulk update settings."""
        return await self.settings_repo.bulk_upsert(settings_dict)
