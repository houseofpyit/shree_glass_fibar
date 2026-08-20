"""Common shared schemas."""

from typing import Any, Optional, List
from pydantic import BaseModel


class StandardResponse(BaseModel):
    """Standard API response."""
    success: bool
    message: str
    data: Any = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    message: str
    errors: List[str] = []


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    success: bool = True
    message: str = "Success"
    data: Any = None
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
