"""App settings schemas."""

from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel


class AppSettingsResponse(BaseModel):
    """Schema for app settings response."""
    id: int
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class AppSettingsUpdate(BaseModel):
    """Schema for updating settings (batch)."""
    settings: Dict[str, str]

    class Config:
        json_schema_extra = {
            "example": {
                "settings": {
                    "youtube_url": "https://youtube.com/@company",
                    "instagram_url": "https://instagram.com/company",
                    "facebook_url": "https://facebook.com/company",
                    "company_name": "Shree Glass Fiber",
                    "support_email": "support@shreeglass.com",
                    "support_phone": "+91-9876543210",
                    "privacy_policy_url": "https://shreeglass.com/privacy",
                    "terms_url": "https://shreeglass.com/terms",
                    "android_min_version": "1.0.0",
                    "ios_min_version": "1.0.0",
                    "force_update": "false",
                    "maintenance_mode": "false"
                }
            }
        }
