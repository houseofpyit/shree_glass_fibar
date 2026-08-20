"""Contact information repository for database operations."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact_information import ContactInformation


class ContactRepository:
    """Repository for ContactInformation model database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self) -> Optional[ContactInformation]:
        """Get contact information (single row)."""
        result = await self.db.execute(
            select(ContactInformation).limit(1)
        )
        return result.scalar_one_or_none()

    async def upsert(self, data: dict) -> ContactInformation:
        """Create or update contact information."""
        contact = await self.get()
        if contact:
            for key, value in data.items():
                if value is not None:
                    setattr(contact, key, value)
        else:
            contact = ContactInformation(**data)
            self.db.add(contact)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact
