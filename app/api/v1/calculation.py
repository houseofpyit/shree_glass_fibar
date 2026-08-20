"""Calculation module endpoint (Coming Soon)."""

from fastapi import APIRouter

from app.core.response import success_response

router = APIRouter()


@router.get(
    "",
    summary="Calculation feature",
    description="Calculation feature - Currently coming soon.",
)
async def get_calculation():
    """Get calculation feature info (Coming Soon)."""
    return success_response(
        data={
            "title": "Calculation",
            "description": "This feature is coming soon. Stay tuned for GFRP rebar calculation tools.",
            "image": None,
        },
        message="Coming Soon",
    )
