"""Standardized API response helpers."""

from typing import Any, Optional, List


def success_response(
    data: Any = None,
    message: str = "Success",
) -> dict:
    """Return a standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str = "An error occurred",
    errors: Optional[List[str]] = None,
) -> dict:
    """Return a standardized error response."""
    return {
        "success": False,
        "message": message,
        "errors": errors or [],
    }
