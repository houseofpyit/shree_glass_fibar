"""CMS page repository for database operations."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cms_page import CMSPage


class CMSRepository:
    """Repository for CMSPage model database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_slug(self, slug: str) -> Optional[CMSPage]:
        """Get a CMS page by slug."""
        result = await self.db.execute(
            select(CMSPage).where(CMSPage.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_active_by_slug(self, slug: str) -> Optional[CMSPage]:
        """Get an active CMS page by slug."""
        result = await self.db.execute(
            select(CMSPage).where(CMSPage.slug == slug, CMSPage.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_all(self, active_only: bool = False) -> List[CMSPage]:
        """Get all CMS pages ordered by display_order."""
        query = select(CMSPage)
        if active_only:
            query = query.where(CMSPage.is_active == True)
        query = query.order_by(CMSPage.display_order.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, page: CMSPage) -> CMSPage:
        """Create a new CMS page."""
        self.db.add(page)
        await self.db.flush()
        await self.db.refresh(page)
        return page

    async def update(self, page_id: int, data: dict) -> Optional[CMSPage]:
        """Update a CMS page."""
        result = await self.db.execute(
            select(CMSPage).where(CMSPage.id == page_id)
        )
        page = result.scalar_one_or_none()
        if page:
            for key, value in data.items():
                if value is not None:
                    setattr(page, key, value)
            await self.db.flush()
            await self.db.refresh(page)
        return page

    async def delete(self, page_id: int) -> bool:
        """Delete a CMS page."""
        result = await self.db.execute(
            select(CMSPage).where(CMSPage.id == page_id)
        )
        page = result.scalar_one_or_none()
        if page:
            await self.db.delete(page)
            await self.db.flush()
            return True
        return False
