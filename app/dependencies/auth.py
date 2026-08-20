"""Authentication dependencies for route protection."""

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, ACCESS_TOKEN
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.models.user import UserStatus

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current authenticated user from JWT token.
    Works for both Super Admin and normal users.
    Returns a dict for Super Admin, or User model for normal users.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != ACCESS_TOKEN:
        raise UnauthorizedException("Invalid token type")

    is_super_admin = payload.get("is_super_admin", False)
    sub = payload.get("sub")

    if not sub:
        raise UnauthorizedException("Invalid token payload")

    # Super Admin — no DB lookup needed
    if is_super_admin:
        from app.config import settings
        return {
            "id": 0,
            "name": "Super Admin",
            "email": settings.SUPER_ADMIN_EMAIL,
            "is_super_admin": True,
            "status": "approved",
        }

    # Normal user — verify in database
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(sub))

    if not user:
        raise UnauthorizedException("User not found")

    if user.status != UserStatus.APPROVED:
        raise ForbiddenException("Account is not active")

    return user


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Require Super Admin access. Returns admin info dict.
    Used to protect admin-only endpoints.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != ACCESS_TOKEN:
        raise UnauthorizedException("Invalid token type")

    is_super_admin = payload.get("is_super_admin", False)
    if not is_super_admin:
        raise ForbiddenException("Admin access required")

    from app.config import settings
    return {
        "id": 0,
        "email": settings.SUPER_ADMIN_EMAIL,
        "is_super_admin": True,
    }
