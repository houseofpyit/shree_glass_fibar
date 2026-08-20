"""Device token schemas for push notifications."""

from pydantic import BaseModel, Field


class DeviceTokenCreate(BaseModel):
    """Schema for registering/updating device token."""
    token: str = Field(..., min_length=1, max_length=500, description="Firebase FCM token")
    platform: str = Field(..., pattern="^(android|ios)$", description="Device platform: android or ios")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "dGhpcyBpcyBhIHNhbXBsZSBGQ00gdG9rZW4...",
                "platform": "android"
            }
        }
