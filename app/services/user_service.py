"""User service for user management operations."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ForbiddenException,
)
from app.models.user import User, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserProfileUpdate


class UserService:
    """Service for user management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_profile(self, user_id: int) -> User:
        """Get user profile."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def update_profile(self, user_id: int, data: UserProfileUpdate) -> User:
        """Update user profile."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        if not verify_password(current_password, user.password):
            raise BadRequestException("Current password is incorrect")

        user.password = hash_password(new_password)
        await self.db.flush()
        return True

    async def get_users_by_status(
        self,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple:
        """Get paginated users with optional filters."""
        return await self.user_repo.get_users_by_status(
            status=status, search=search, page=page, page_size=page_size
        )

    async def change_user_status(self, user_id: int, status: str) -> User:
        """Approve, reject, or suspend a user via a single status value."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        new_status = UserStatus(status)
        if user.status == new_status:
            raise BadRequestException(f"User is already {new_status.value}")

        return await self.user_repo.update_status(user_id, new_status)

    async def soft_delete_user(self, user_id: int) -> bool:
        """Soft delete a user."""
        return await self.user_repo.soft_delete(user_id)

    async def get_dashboard_counts(self) -> dict:
        """Get dashboard counts."""
        return await self.user_repo.get_dashboard_counts()
