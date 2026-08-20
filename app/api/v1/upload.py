"""File upload endpoints."""

from fastapi import APIRouter, Depends, UploadFile, File

from app.dependencies.auth import get_current_admin
from app.services.upload_service import UploadService
from app.schemas.common import StandardResponse
from app.core.response import success_response

router = APIRouter()


@router.post(
    "/image",
    response_model=StandardResponse,
    summary="Upload image",
    description="Upload an image file (JPEG, PNG, WebP, GIF). Max size configurable. Admin only.",
    status_code=201,
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    admin: dict = Depends(get_current_admin),
):
    """Upload an image file."""
    url = await UploadService.upload_image(file)
    return success_response(data={"url": url}, message="Image uploaded successfully")


@router.post(
    "/pdf",
    response_model=StandardResponse,
    summary="Upload PDF",
    description="Upload a PDF file. Max size configurable. Admin only.",
    status_code=201,
)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to upload"),
    admin: dict = Depends(get_current_admin),
):
    """Upload a PDF file."""
    url = await UploadService.upload_pdf(file)
    return success_response(data={"url": url}, message="PDF uploaded successfully")
