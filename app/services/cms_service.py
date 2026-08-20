"""CMS service for content management operations."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.cms_page import CMSPage
from app.repositories.cms_repository import CMSRepository
from app.schemas.cms import CMSPageCreate, CMSPageUpdate
from app.services.upload_service import UploadService
from fastapi import UploadFile


class CMSService:
    """Service for CMS operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.cms_repo = CMSRepository(db)

    async def get_page_by_slug(self, slug: str) -> CMSPage:
        """Get an active CMS page by slug."""
        page = await self.cms_repo.get_active_by_slug(slug)
        if not page:
            raise NotFoundException(f"Page '{slug}' not found")
        return page

    async def get_all_pages(self, active_only: bool = True) -> List[CMSPage]:
        """Get all CMS pages."""
        return await self.cms_repo.get_all(active_only=active_only)

    async def create_page(
        self,
        data: CMSPageCreate,
        image: Optional[UploadFile] = None,
        pdf: Optional[UploadFile] = None,
    ) -> CMSPage:
        """Create a new CMS page."""

        existing = await self.cms_repo.get_by_slug(data.slug)

        if existing:
            raise ConflictException(
                f"Page with slug '{data.slug}' already exists"
            )

        page_data = data.model_dump()

        if self._has_upload(image):
            page_data["image"] = await self._upload_image(image)

        if self._has_upload(pdf):
            page_data["pdf"] = await self._upload_pdf(pdf)

        page = CMSPage(**page_data)

        return await self.cms_repo.create(page)

    async def update_page(
        self,
        page_id: int,
        data: CMSPageUpdate,
        image: Optional[UploadFile] = None,
        pdf: Optional[UploadFile] = None,
    ) -> CMSPage:
        """Update a CMS page."""

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Check slug uniqueness if slug is being updated
        if "slug" in update_data:
            existing = await self.cms_repo.get_by_slug(update_data["slug"])

            if existing and existing.id != page_id:
                raise ConflictException(
                    f"Page with slug '{update_data['slug']}' already exists"
                )

        if self._has_upload(image):
            update_data["image"] = await self._upload_image(image)

        if self._has_upload(pdf):
            update_data["pdf"] = await self._upload_pdf(pdf)

        if not update_data:
            raise BadRequestException(
                "No data to update. Send JSON or multipart form fields "
                "(title, slug, description, image, pdf, ...)."
            )

        page = await self.cms_repo.update(
            page_id,
            update_data,
        )

        if not page:
            raise NotFoundException("Page not found")

        return page

    async def delete_page(self, page_id: int) -> bool:
        """Delete a CMS page."""
        deleted = await self.cms_repo.delete(page_id)
        if not deleted:
            raise NotFoundException("Page not found")
        return True

    @staticmethod
    def _has_upload(file: Optional[UploadFile]) -> bool:
        """Treat empty multipart file fields as omitted."""
        return file is not None and bool(file.filename)

    async def _upload_image(self, file: UploadFile) -> str:
        """Upload an image file and return the stored relative path."""
        return await UploadService.upload_image(file)

    async def _upload_pdf(self, file: UploadFile) -> str:
        """Upload a PDF file and return the stored relative path."""
        return await UploadService.upload_pdf(file)


