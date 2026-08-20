"""User-related schemas with validation."""

import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, Field


class UserCreate(BaseModel):
    """Schema for user registration."""
    personal_name: str = Field(..., min_length=2, max_length=255, description="Full name of the user")
    mobile: str = Field(..., min_length=10, max_length=15, description="Indian mobile number")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")
    business_name: Optional[str] = Field(None, max_length=255, description="Business name (optional)")
    gst_number: Optional[str] = Field(None, max_length=15, description="GST number in Indian format (optional)")
    address: Optional[str] = Field(None, max_length=500, description="Address (optional)")

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        """Validate Indian mobile number format."""
        cleaned = re.sub(r"[\s\-]", "", v)
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError("Invalid Indian mobile number. Must be 10 digits starting with 6-9.")
        return cleaned

    @field_validator("gst_number")
    @classmethod
    def validate_gst(cls, v: Optional[str]) -> Optional[str]:
        """Validate Indian GST number format."""
        if v is None or v == "":
            return None
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(pattern, v.upper()):
            raise ValueError("Invalid GST number format. Expected format: 22AAAAA0000A1Z5")
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "personal_name": "Rahul Sharma",
                "mobile": "9876543210",
                "email": "rahul@example.com",
                "password": "SecurePass@123",
                "business_name": "Sharma Constructions",
                "gst_number": "22AAAAA0000A1Z5",
                "address": "123 Main Street, Mumbai"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login (email or mobile)."""
    identifier: str = Field(..., description="Email or mobile number")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "identifier": "rahul@example.com",
                "password": "SecurePass@123"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    personal_name: str
    mobile: str
    email: str
    business_name: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list (admin)."""
    id: int
    personal_name: str
    mobile: str
    email: str
    business_name: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    personal_name: Optional[str] = Field(None, min_length=2, max_length=255)
    business_name: Optional[str] = Field(None, max_length=255)
    gst_number: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=500)

    @field_validator("gst_number")
    @classmethod
    def validate_gst(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(pattern, v.upper()):
            raise ValueError("Invalid GST number format.")
        return v.upper()


class UserStatusUpdate(BaseModel):
    """Schema for admin approve / reject / suspend in one request."""
    status: str = Field(
        ...,
        description="New status: approved, rejected, or suspended",
        examples=["approved"],
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"approved", "rejected", "suspended"}
        normalized = v.strip().lower()
        if normalized not in allowed:
            raise ValueError("status must be one of: approved, rejected, suspended")
        return normalized

    class Config:
        json_schema_extra = {
            "example": {"status": "approved"}
        }


class ChangePasswordRequest(BaseModel):
    """Schema for change password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password - request OTP."""
    email: EmailStr = Field(..., description="Registered email address")


class ResetPasswordRequest(BaseModel):
    """Schema for reset password with OTP."""
    email: EmailStr = Field(..., description="Registered email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
