"""Admin panel endpoints."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_admin
from app.services.user_service import UserService
from app.repositories.audit_repository import AuditRepository
from app.models.user import UserStatus
from app.schemas.common import StandardResponse, PaginatedResponse
from app.schemas.user import UserListResponse, ChangePasswordRequest, UserStatusUpdate
from app.core.response import success_response
from app.core.security import hash_password, verify_password
from app.config import settings

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=StandardResponse,
    summary="Admin dashboard",
    description="Get dashboard statistics including user counts by status.",
)
async def dashboard(
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get admin dashboard statistics."""
    user_service = UserService(db)
    counts = await user_service.get_dashboard_counts()
    return success_response(data=counts, message="Dashboard data")


@router.get(
    "/users",
    response_model=PaginatedResponse,
    summary="List users",
    description="Get paginated list of users with optional status filter and search.",
)
async def list_users(
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name, email, mobile, or business"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of users."""
    user_service = UserService(db)
    users, total = await user_service.get_users_by_status(
        status=status, search=search, page=page, page_size=page_size
    )
    user_data = [UserListResponse.model_validate(u).model_dump() for u in users]
    return {
        "success": True,
        "message": "Users retrieved",
        "data": user_data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.put(
    "/users/{user_id}/status",
    response_model=StandardResponse,
    summary="Change user status",
    description="Approve, reject, or suspend a user by sending status in the body.",
)
async def change_user_status(
    user_id: int,
    data: UserStatusUpdate,
    request: Request,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Approve, reject, or suspend a user with one API."""
    user_service = UserService(db)
    user = await user_service.change_user_status(user_id, data.status)

    audit_repo = AuditRepository(db)
    await audit_repo.create(
        actor_email=admin["email"],
        action=f"{data.status}_user",
        resource_type="user",
        resource_id=str(user_id),
        details=f"Status changed to {data.status}",
        ip_address=request.client.host if request.client else None,
    )

    return success_response(
        message=f"User '{user.personal_name}' {data.status}",
        data={"id": user.id, "status": user.status.value},
    )


@router.delete(
    "/users/{user_id}",
    response_model=StandardResponse,
    summary="Delete user (soft)",
    description="Soft delete a user. The user record is preserved but marked as deleted.",
)
async def delete_user(
    user_id: int,
    request: Request,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a user."""
    user_service = UserService(db)
    await user_service.soft_delete_user(user_id)

    audit_repo = AuditRepository(db)
    await audit_repo.create(
        actor_email=admin["email"],
        action="delete_user",
        resource_type="user",
        resource_id=str(user_id),
        ip_address=request.client.host if request.client else None,
    )

    return success_response(message="User deleted")


@router.get(
    "/audit-logs",
    response_model=StandardResponse,
    summary="Get audit logs",
    description="Get recent admin action audit logs.",
)
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get recent audit logs."""
    audit_repo = AuditRepository(db)
    logs = await audit_repo.get_recent(limit=limit)
    log_data = [
        {
            "id": log.id,
            "actor_email": log.actor_email,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
    return success_response(data=log_data, message="Audit logs retrieved")


@router.put(
    "/change-password",
    response_model=StandardResponse,
    summary="Admin change password",
    description="Change the super admin password (updates .env conceptually; in production use env management).",
)
async def admin_change_password(
    data: ChangePasswordRequest,
    admin: dict = Depends(get_current_admin),
):
    """
    Change admin password.
    Note: In production, admin password should be managed via environment variables.
    This endpoint validates the current password but cannot persist changes to .env.
    """
    if data.current_password != settings.SUPER_ADMIN_PASSWORD:
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Current password is incorrect")

    # In a real deployment, you'd update the password in a secrets manager
    # For now, we acknowledge the limitation
    return success_response(
        message="Password change acknowledged. Please update SUPER_ADMIN_PASSWORD in your environment variables."
    )
