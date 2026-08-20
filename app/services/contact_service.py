"""Contact information service."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.contact_information import ContactInformation
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactInfoUpdate


class ContactService:
    """Service for contact information operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.contact_repo = ContactRepository(db)

    async def get_contact_info(self) -> Optional[ContactInformation]:
        """Get contact information."""
        contact = await self.contact_repo.get()
        if not contact:
            raise NotFoundException("Contact information not configured")
        return contact

    async def update_contact_info(self, data: ContactInfoUpdate) -> ContactInformation:
        """Update contact information."""
        update_data = data.model_dump(exclude_unset=True)
        return await self.contact_repo.upsert(update_data)
