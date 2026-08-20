"""CMS endpoints for content management."""

from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.cms_service import CMSService
from app.repositories.audit_repository import AuditRepository
from app.schemas.cms import CMSPageCreate, CMSPageUpdate, CMSPageResponse, to_public_url
from app.schemas.common import StandardResponse
from app.core.response import success_response
from app.core.exceptions import BadRequestException

router = APIRouter()

_CMS_TEXT_FIELDS = (
    "title",
    "slug",
    "description",
    "display_order",
    "image_alt",
    "is_active",
    "meta_title",
    "meta_description",
)


def _parse_bool(value, default: Optional[bool] = None) -> Optional[bool]:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().strip("\"'").lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    return default


def _parse_int(value, default: Optional[int] = None) -> Optional[int]:
    if value is None or value == "":
        return default
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    try:
        return int(str(value).strip().strip("\"'"))
    except ValueError:
        return default


def _clean_str(value) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().strip("\"'")
    return text if text else None


def _serialize_page(page, request: Request) -> dict:
    """Serialize a CMS page with public image/PDF URLs for the request host."""
    data = CMSPageResponse.model_validate(page).model_dump()
    base_url = str(request.base_url).rstrip("/")
    data["image"] = to_public_url(page.image, base_url=base_url)
    data["pdf"] = to_public_url(page.pdf, base_url=base_url)
    return data


def _is_upload(value) -> bool:
    return isinstance(value, (UploadFile, StarletteUploadFile)) and bool(
        getattr(value, "filename", None)
    )


def _normalize_payload(raw: dict) -> dict:
    payload = {}
    if "title" in raw:
        payload["title"] = _clean_str(raw.get("title"))
    if "slug" in raw:
        payload["slug"] = _clean_str(raw.get("slug"))
    if "description" in raw:
        payload["description"] = _clean_str(raw.get("description"))
    if "image_alt" in raw:
        payload["image_alt"] = _clean_str(raw.get("image_alt"))
    if "meta_title" in raw:
        payload["meta_title"] = _clean_str(raw.get("meta_title"))
    if "meta_description" in raw:
        payload["meta_description"] = _clean_str(raw.get("meta_description"))
    if "display_order" in raw:
        payload["display_order"] = _parse_int(raw.get("display_order"), 0)
    if "is_active" in raw:
        payload["is_active"] = _parse_bool(raw.get("is_active"), True)
    if "image" in raw and isinstance(raw["image"], str) and raw["image"]:
        payload["image"] = _clean_str(raw["image"])
    if "pdf" in raw and isinstance(raw["pdf"], str) and raw["pdf"]:
        payload["pdf"] = _clean_str(raw["pdf"])
    return {k: v for k, v in payload.items() if v is not None}


async def _parse_cms_body(
    request: Request,
) -> Tuple[dict, Optional[UploadFile], Optional[UploadFile]]:
    """Accept JSON or multipart/form-data (including image and pdf files)."""
    content_type = (request.headers.get("content-type") or "").lower()

    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception as exc:
            raise BadRequestException("Invalid JSON body") from exc
        if not isinstance(body, dict):
            raise BadRequestException("JSON body must be an object")
        return _normalize_payload(body), None, None

    form = await request.form()
    raw = {}
    image = None
    pdf = None

    for key in _CMS_TEXT_FIELDS:
        if key in form:
            raw[key] = form.get(key)

    image_val = form.get("image")
    pdf_val = form.get("pdf")

    if _is_upload(image_val):
        image = image_val
    elif isinstance(image_val, str) and image_val.strip():
        raw["image"] = image_val

    if _is_upload(pdf_val):
        pdf = pdf_val
    elif isinstance(pdf_val, str) and pdf_val.strip():
        raw["pdf"] = pdf_val

    return _normalize_payload(raw), image, pdf


# Public CMS endpoints
@router.get(
    "/pages",
    response_model=StandardResponse,
    summary="Get all active CMS pages",
    description="Get all active CMS pages for the mobile app. Public — no auth required.",
)
async def get_all_pages(request: Request, db: AsyncSession = Depends(get_db)):
    """Get all active CMS pages."""
    cms_service = CMSService(db)
    pages = await cms_service.get_all_pages(active_only=True)
    page_data = [_serialize_page(p, request) for p in pages]
    return success_response(data=page_data, message="CMS pages retrieved")


@router.get(
    "/{slug}",
    response_model=StandardResponse,
    summary="Get CMS page by slug",
    description="Get a specific CMS page content by its slug. Public — no auth required.",
)
async def get_page_by_slug(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Get a CMS page by slug."""
    cms_service = CMSService(db)
    page = await cms_service.get_page_by_slug(slug)
    page_data = _serialize_page(page, request)
    return success_response(data=page_data, message="Page retrieved")


# Admin CMS endpoints
@router.get(
    "/admin/all",
    response_model=StandardResponse,
    summary="Get all CMS pages (admin)",
    description="Get all CMS pages including inactive ones. Admin only.",
)
async def admin_get_all_pages(
    request: Request,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all CMS pages (including inactive) for admin."""
    cms_service = CMSService(db)
    pages = await cms_service.get_all_pages(active_only=False)
    page_data = [_serialize_page(p, request) for p in pages]
    return success_response(data=page_data, message="All CMS pages retrieved")


@router.post(
    "/admin/create",
    response_model=StandardResponse,
    summary="Create CMS page",
    description="Create a new CMS page. Accepts JSON or multipart form (image/pdf). Admin only.",
    status_code=201,
)
async def create_page(
    request: Request,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new CMS page (JSON or multipart form)."""
    raw, image, pdf = await _parse_cms_body(request)
    data = CMSPageCreate.model_validate(raw)

    cms_service = CMSService(db)
    page = await cms_service.create_page(data=data, image=image, pdf=pdf)

    audit_repo = AuditRepository(db)
    await audit_repo.create(
        actor_email=admin["email"],
        action="create_cms_page",
        resource_type="cms_page",
        resource_id=str(page.id),
        details=f"Created page: {page.title}",
        ip_address=request.client.host if request.client else None,
    )

    return success_response(
        data=_serialize_page(page, request),
        message="CMS page created",
    )


@router.put(
    "/admin/{page_id}",
    response_model=StandardResponse,
    summary="Update CMS page",
    description="Update an existing CMS page. Accepts JSON or multipart form (image/pdf). Admin only.",
)
async def update_page(
    page_id: int,
    request: Request,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a CMS page (JSON or multipart form with optional image/PDF)."""
    raw, image, pdf = await _parse_cms_body(request)
    data = CMSPageUpdate.model_validate(raw)

    cms_service = CMSService(db)
    page = await cms_service.update_page(
        page_id=page_id,
        data=data,
        image=image,
        pdf=pdf,
    )

    audit_repo = AuditRepository(db)
    await audit_repo.create(
        actor_email=admin["email"],
        action="update_cms_page",
        resource_type="cms_page",
        resource_id=str(page_id),
        details=f"Updated page: {page.title}",
        ip_address=request.client.host if request.client else None,
    )

    return success_response(
        data=_serialize_page(page, request),
        message="CMS page updated",
    )


@router.delete(
    "/admin/{page_id}",
    response_model=StandardResponse,
    summary="Delete CMS page",
    description="Delete a CMS page. Admin only.",
)
async def delete_page(
    page_id: int,
    request: Request,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a CMS page."""
    cms_service = CMSService(db)
    await cms_service.delete_page(page_id)

    audit_repo = AuditRepository(db)
    await audit_repo.create(
        actor_email=admin["email"],
        action="delete_cms_page",
        resource_type="cms_page",
        resource_id=str(page_id),
        ip_address=request.client.host if request.client else None,
    )

    return success_response(message="CMS page deleted")
