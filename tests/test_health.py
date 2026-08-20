"""Health check endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health endpoint returns healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_structure(client: AsyncClient):
    """Test health response follows standard response format."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "success" in data
    assert "message" in data
    assert "data" in data
