"""Audit log repository for database operations."""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepository:
    """Repository for AuditLog model database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        actor_email: str,
        action: str,
        resource_type: str,
        resource_id: str = None,
        details: str = None,
        ip_address: str = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        log = AuditLog(
            actor_email=actor_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def get_recent(self, limit: int = 50) -> List[AuditLog]:
        """Get recent audit logs."""
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
