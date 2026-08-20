"""CMS page schemas."""

from typing import Optional
from datetime import datetime
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator

from app.config import settings

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def to_public_url(path: Optional[str], base_url: Optional[str] = None) -> Optional[str]:
    """Convert a stored relative path (or local absolute URL) to a full public URL."""
    if not path:
        return path
    base = (base_url or settings.BASE_URL).rstrip("/")
    if path.startswith(("http://", "https://")):
        parsed = urlparse(path)
        if parsed.hostname in _LOCAL_HOSTS:
            return f"{base}{parsed.path}"
        return path
    if path.startswith("/"):
        return f"{base}{path}"
    return f"{base}/{path}"


class CMSPageResponse(BaseModel):
    """Schema for CMS page response."""
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    image_alt: Optional[str] = None
    pdf: Optional[str] = None
    display_order: int
    is_active: bool
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator("image", "pdf")
    @classmethod
    def make_public_url(cls, v: Optional[str]) -> Optional[str]:
        """Return full public URL for image and PDF paths."""
        return to_public_url(v)


class CMSPageCreate(BaseModel):
    """Schema for creating a CMS page."""
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    image: Optional[str] = None
    image_alt: Optional[str] = Field(None, max_length=255)
    pdf: Optional[str] = None
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "About GFRP",
                "slug": "about",
                "description": "<p>GFRP rebar information...</p>",
                "image": "/uploads/images/about.jpg",
                "image_alt": "About GFRP Rebar",
                "display_order": 1,
                "is_active": True,
                "meta_title": "About GFRP - Shree Glass Fiber",
                "meta_description": "Learn about GFRP rebar technology"
            }
        }


class CMSPageUpdate(BaseModel):
    """Schema for updating a CMS page."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    image: Optional[str] = None
    image_alt: Optional[str] = Field(None, max_length=255)
    pdf: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
