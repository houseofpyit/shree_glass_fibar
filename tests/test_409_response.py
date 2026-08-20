"""Verify 409 Conflict responses include a `message` field."""

import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_message(client: AsyncClient):
    """Registering with an existing email should return 409 with a message field."""
    unique = str(int(time.time()))
    payload = {
        "personal_name": "Test User",
        "mobile": f"9{unique[-9:]}",
        "email": f"duplicate{unique}@example.com",
        "password": "password123",
        "business_name": "Test Business",
        "gst_number": "22AAAAA0000A1Z5",
        "address": "Test Address",
    }

    # First registration succeeds
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    # Second registration with same email → 409 Conflict
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409

    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Email already registered"
    assert body["errors"] == []
