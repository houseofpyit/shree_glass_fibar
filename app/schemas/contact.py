"""Contact information schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ContactInfoResponse(BaseModel):
    """Schema for contact information response."""
    id: int
    office_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    google_map_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactInfoUpdate(BaseModel):
    """Schema for updating contact information."""
    office_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = Field(None, max_length=1000)
    google_map_url: Optional[str] = Field(None, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "office_name": "Shree Glass Fiber Pvt. Ltd.",
                "phone": "+91-9876543210",
                "email": "info@shreeglass.com",
                "website": "https://shreeglass.com",
                "address": "123 Industrial Area, Gujarat, India",
                "google_map_url": "https://maps.google.com/..."
            }
        }
