"""Authentication endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_validation_error(client: AsyncClient):
    """Test registration with invalid data returns validation error."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "personal_name": "T",  # Too short
            "mobile": "123",  # Invalid
            "email": "invalid-email",
            "password": "short",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_login_missing_fields(client: AsyncClient):
    """Test login with missing fields."""
    response = await client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_admin_login_invalid_credentials(client: AsyncClient):
    """Test admin login with wrong credentials."""
    response = await client.post(
        "/api/v1/auth/admin/login",
        json={"email": "wrong@email.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """Test refresh with invalid token."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout endpoint."""
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
