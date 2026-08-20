"""User repository for database operations."""

from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus


class UserRepository:
    """Repository for User model database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        """Create a new user."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID (excluding soft-deleted)."""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email (excluding soft-deleted)."""
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_by_mobile(self, mobile: str) -> Optional[User]:
        """Get user by mobile (excluding soft-deleted)."""
        result = await self.db.execute(
            select(User).where(User.mobile == mobile, User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_by_email_or_mobile(self, identifier: str) -> Optional[User]:
        """Get user by email or mobile (excluding soft-deleted)."""
        result = await self.db.execute(
            select(User).where(
                or_(User.email == identifier, User.mobile == identifier),
                User.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_users_by_status(
        self,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[User], int]:
        """Get paginated users with optional status filter and search."""
        query = select(User).where(User.is_deleted == False)

        if status:
            query = query.where(User.status == status)

        if search:
            search_filter = or_(
                User.personal_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.mobile.ilike(f"%{search}%"),
                User.business_name.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(User.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def update_status(self, user_id: int, status: UserStatus) -> Optional[User]:
        """Update user status."""
        user = await self.get_by_id(user_id)
        if user:
            user.status = status
            await self.db.flush()
            await self.db.refresh(user)
        return user

    async def soft_delete(self, user_id: int) -> bool:
        """Soft delete a user."""
        user = await self.get_by_id(user_id)
        if user:
            user.is_deleted = True
            await self.db.flush()
            return True
        return False

    async def get_dashboard_counts(self) -> dict:
        """Get user counts by status for dashboard."""
        result = await self.db.execute(
            select(User.status, func.count(User.id))
            .where(User.is_deleted == False)
            .group_by(User.status)
        )
        counts = {status.value: 0 for status in UserStatus}
        for status, count in result.all():
            counts[status.value] = count
        counts["total"] = sum(counts.values())
        return counts
