"""Authentication service — single login flow for both admin and users."""

import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    REFRESH_TOKEN,
)
from app.core.exceptions import (
    UnauthorizedException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
)
from app.models.user import User, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: UserCreate) -> User:
        """Register a new user."""
        # Check duplicate email
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictException("Email already registered")

        # Check duplicate mobile
        existing = await self.user_repo.get_by_mobile(data.mobile)
        if existing:
            raise ConflictException("Mobile number already registered")

        # Create user
        user = User(
            personal_name=data.personal_name,
            mobile=data.mobile,
            email=data.email.lower(),
            password=hash_password(data.password),
            business_name=data.business_name,
            gst_number=data.gst_number,
            address=data.address,
            status=UserStatus.PENDING,
        )
        return await self.user_repo.create(user)

    async def login(self, username: str, password: str) -> dict:
        """
        Unified login: checks Super Admin first, then falls back to database users.
        Returns tokens + user info with is_super_admin flag.
        """
        # Step 1: Check if credentials match Super Admin from .env
        if username.lower() == settings.SUPER_ADMIN_EMAIL.lower():
            if password == settings.SUPER_ADMIN_PASSWORD:
                # Authenticate as Super Admin
                token_data = {"sub": "super_admin", "is_super_admin": True}
                access_token = create_access_token(token_data)
                refresh_token = create_refresh_token(token_data)

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "Bearer",
                    "user": {
                        "id": 0,
                        "name": "Super Admin",
                        "email": settings.SUPER_ADMIN_EMAIL,
                        "is_super_admin": True,
                        "status": "approved",
                    },
                }

        # Step 2: Authenticate against users table
        user = await self.user_repo.get_by_email_or_mobile(username)
        if not user:
            raise UnauthorizedException("Invalid credentials")

        if not verify_password(password, user.password):
            raise UnauthorizedException("Invalid credentials")

        if user.status == UserStatus.PENDING:
            raise ForbiddenException(
                "Your profile has been submitted successfully. "
                "Our team will review your profile. Once approved, you can login."
            )
        elif user.status == UserStatus.REJECTED:
            raise ForbiddenException("Your account has been rejected. Please contact support.")
        elif user.status == UserStatus.SUSPENDED:
            raise ForbiddenException("Your account has been suspended. Please contact support.")

        # Generate tokens for normal user
        token_data = {"sub": str(user.id), "is_super_admin": False}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "user": {
                "id": user.id,
                "name": user.personal_name,
                "email": user.email,
                "is_super_admin": False,
                "status": user.status.value,
            },
        }

    async def refresh_token(self, refresh_token_str: str) -> dict:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token_str)
        if not payload:
            raise UnauthorizedException("Invalid or expired refresh token")

        if payload.get("type") != REFRESH_TOKEN:
            raise UnauthorizedException("Invalid token type")

        # Generate new tokens preserving claims
        token_data = {
            "sub": payload["sub"],
            "is_super_admin": payload.get("is_super_admin", False),
        }
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
        }

    async def forgot_password(self, email: str) -> str:
        """Generate OTP for password reset."""
        user = await self.user_repo.get_by_email(email.lower())
        if not user:
            raise BadRequestException("No account found with this email")

        # Generate 6-digit OTP
        otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        user.reset_otp = otp
        user.reset_otp_expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        await self.db.flush()

        # TODO: Send OTP via email (pluggable provider)
        return otp

    async def reset_password(self, email: str, otp: str, new_password: str) -> bool:
        """Reset password using OTP."""
        user = await self.user_repo.get_by_email(email.lower())
        if not user:
            raise BadRequestException("No account found with this email")

        if not user.reset_otp or user.reset_otp != otp:
            raise BadRequestException("Invalid OTP")

        if user.reset_otp_expires and user.reset_otp_expires < datetime.now(timezone.utc):
            raise BadRequestException("OTP has expired")

        user.password = hash_password(new_password)
        user.reset_otp = None
        user.reset_otp_expires = None
        await self.db.flush()
        return True
