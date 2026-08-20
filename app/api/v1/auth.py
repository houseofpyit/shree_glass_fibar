"""Authentication endpoints — single unified login."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.auth import LoginRequest, RefreshTokenRequest
from app.schemas.common import StandardResponse
from app.core.response import success_response

router = APIRouter()


@router.post(
    "/register",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account. Account will be in 'pending' status until approved by admin.",
)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user. Status will be 'pending' until admin approval."""
    auth_service = AuthService(db)
    await auth_service.register(data)
    return success_response(
        message=(
            "Your profile has been submitted successfully. "
            "Our team will review your profile. Once approved, you can login."
        )
    )


@router.post(
    "/login",
    response_model=StandardResponse,
    summary="Login",
    description=(
        "Single login endpoint for both Super Admin and normal users. "
        "Checks Super Admin credentials from environment first, then falls back to database. "
        "Returns is_super_admin flag for Flutter to determine which UI to display."
    ),
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Unified login for Super Admin and normal users.

    - If credentials match Super Admin (.env): returns is_super_admin=true
    - If credentials match an approved user: returns is_super_admin=false
    - Pending/rejected/suspended users receive appropriate error messages.
    """
    auth_service = AuthService(db)
    result = await auth_service.login(data.username, data.password)
    return success_response(data=result, message="Login successful")


@router.post(
    "/refresh",
    response_model=StandardResponse,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token.",
)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token."""
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_token(data.refresh_token)
    return success_response(data=tokens, message="Token refreshed")


@router.post(
    "/logout",
    response_model=StandardResponse,
    summary="Logout",
    description="Logout the current user. Client should discard tokens.",
)
async def logout():
    """Logout (client-side token invalidation)."""
    return success_response(message="Logged out successfully")


@router.post(
    "/forgot-password",
    response_model=StandardResponse,
    summary="Forgot password",
    description="Request a password reset OTP via email.",
)
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request password reset OTP."""
    auth_service = AuthService(db)
    otp = await auth_service.forgot_password(data.email)
    response_data = None
    from app.config import settings
    if not settings.is_production:
        response_data = {"otp": otp}
    return success_response(
        data=response_data,
        message="OTP sent to your registered email address",
    )


@router.post(
    "/reset-password",
    response_model=StandardResponse,
    summary="Reset password",
    description="Reset password using the OTP received via email.",
)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password with OTP."""
    auth_service = AuthService(db)
    await auth_service.reset_password(data.email, data.otp, data.new_password)
    return success_response(message="Password reset successfully")
