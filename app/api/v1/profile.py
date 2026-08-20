"""User profile endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import (
    UserProfileUpdate,
    UserResponse,
    ChangePasswordRequest,
)
from app.schemas.common import StandardResponse
from app.core.response import success_response


router = APIRouter()


@router.get(
    "",
    response_model=StandardResponse,
    summary="Get profile",
    description="Get the current authenticated user's profile.",
)
async def get_profile(
    current_user=Depends(get_current_user),
):
    """Get current authenticated user profile."""

    # Super Admin is returned as a dict from get_current_user()
    if isinstance(current_user, dict) and current_user.get("is_super_admin"):
        user_data = {
            "id": current_user.get("id", 0),
            "name": current_user.get("name", "Super Admin"),
            "personal_name": current_user.get("name", "Super Admin"),
            "email": current_user.get("email"),
            "mobile": None,
            "is_super_admin": True,
            "status": current_user.get("status", "approved"),
            "created_at": None,
            "updated_at": None,
        }

        return success_response(
            data=user_data,
            message="Profile retrieved",
        )

    # Normal User
    user_data = UserResponse.model_validate(current_user).model_dump()

    return success_response(
        data=user_data,
        message="Profile retrieved",
    )


@router.put(
    "",
    response_model=StandardResponse,
    summary="Update profile",
    description="Update the current authenticated user's profile information.",
)
async def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""

    # Super Admin profile is configuration-based and cannot be
    # updated through the normal user profile service.
    if isinstance(current_user, dict) and current_user.get("is_super_admin"):
        return success_response(
            message="Super Admin profile cannot be updated",
        )

    user_service = UserService(db)

    user = await user_service.update_profile(
        current_user.id,
        data,
    )

    user_data = UserResponse.model_validate(user).model_dump()

    return success_response(
        data=user_data,
        message="Profile updated",
    )


@router.put(
    "/change-password",
    response_model=StandardResponse,
    summary="Change password",
    description="Change the current user's password.",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the current user's password."""

    # Super Admin password is configuration-based.
    if isinstance(current_user, dict) and current_user.get("is_super_admin"):
        return success_response(
            message="Super Admin password cannot be changed through this endpoint",
        )

    user_service = UserService(db)

    await user_service.change_password(
        current_user.id,
        data.current_password,
        data.new_password,
    )

    return success_response(
        message="Password changed successfully",
    )