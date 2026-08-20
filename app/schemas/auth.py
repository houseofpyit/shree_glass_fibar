"""Authentication schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema for unified login (admin + user)."""
    username: str = Field(..., description="Email or mobile number")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin@shreeglass.com",
                "password": "SuperAdmin@123"
            }
        }


class LoginUserInfo(BaseModel):
    """User info returned with login response."""
    id: int
    name: str
    email: str
    is_super_admin: bool
    status: str


class LoginResponseData(BaseModel):
    """Login response data containing tokens and user info."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user: LoginUserInfo


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing access token."""
    refresh_token: str = Field(..., description="Valid refresh token")
