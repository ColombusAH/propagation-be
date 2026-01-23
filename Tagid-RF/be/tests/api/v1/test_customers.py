"""
Tests for user registration and login (customer flow).
"""

import pytest
from app.core.config import settings
from httpx import AsyncClient

pytestmark = pytest.mark.skip(reason="Integration tests require DB connection")


@pytest.mark.asyncio
async def test_register_and_login(async_client: AsyncClient):
    """Register a new customer and then login with the credentials.
    Steps:
    1. POST /auth/register with role CUSTOMER.
    2. Ensure registration returns a token.
    3. POST /auth/login with same email/password.
    4. Verify login returns a token and user_id.
    """
    email = "test_customer@example.com"
    password = "StrongP@ssw0rd"
    # Register
    reg_resp = await async_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "Test Customer",
            "phone": "1234567890",
            "address": "Test Address",
            "businessId": None,
            "role": "CUSTOMER",
        },
    )
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "token" in reg_data
    # Login
    login_resp = await async_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "token" in login_data
    assert login_data["user_id"] == reg_data["user_id"]
