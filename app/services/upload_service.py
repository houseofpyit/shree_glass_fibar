"""File upload service."""

import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile

from app.config import settings
from app.core.exceptions import BadRequestException

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_PDF_TYPES = {"application/pdf"}
ALLOWED_PDF_EXTS = {".pdf"}


class UploadService:
    """Service for file upload operations."""

    @staticmethod
    async def upload_image(file: UploadFile) -> str:
        """Upload an image file and return the public URL path."""
        ext = Path(file.filename).suffix.lower() if file.filename else ""
        if file.content_type not in ALLOWED_IMAGE_TYPES and ext not in ALLOWED_IMAGE_EXTS:
            raise BadRequestException(
                f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )

        # Check file size
        content = await file.read()
        max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        if len(content) > max_size:
            raise BadRequestException(
                f"File size exceeds {settings.MAX_IMAGE_SIZE_MB}MB limit"
            )

        # Generate unique filename
        ext = Path(file.filename).suffix if file.filename else ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        upload_dir = Path(settings.UPLOAD_PATH) / "images"
        upload_dir.mkdir(parents=True, exist_ok=True)

        filepath = upload_dir / filename
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        return f"/{settings.UPLOAD_PATH}/images/{filename}"

    @staticmethod
    async def upload_pdf(file: UploadFile) -> str:
        """Upload a PDF file and return the public URL path."""
        ext = Path(file.filename).suffix.lower() if file.filename else ""
        if file.content_type not in ALLOWED_PDF_TYPES and ext not in ALLOWED_PDF_EXTS:
            raise BadRequestException("Invalid file type. Only PDF files are allowed.")

        # Check file size
        content = await file.read()
        max_size = settings.MAX_PDF_SIZE_MB * 1024 * 1024
        if len(content) > max_size:
            raise BadRequestException(
                f"File size exceeds {settings.MAX_PDF_SIZE_MB}MB limit"
            )

        # Generate unique filename
        ext = Path(file.filename).suffix if file.filename else ".pdf"
        filename = f"{uuid.uuid4().hex}{ext}"
        upload_dir = Path(settings.UPLOAD_PATH) / "pdfs"
        upload_dir.mkdir(parents=True, exist_ok=True)

        filepath = upload_dir / filename
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        return f"/{settings.UPLOAD_PATH}/pdfs/{filename}"
