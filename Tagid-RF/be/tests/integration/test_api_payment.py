"""
Integration tests for payment API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_payment_intent(async_client: AsyncClient, auth_headers):
    """Test creating a payment intent."""
    response = await async_client.post(
        "/api/v1/payment/create-intent",
        headers=auth_headers,
        json={
            "amount": 10000,  # 100 ILS in agorot
            "currency": "ILS",
            "provider": "STRIPE",
            "tagIds": [],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "paymentId" in data
    assert "clientSecret" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_cash_payment(async_client: AsyncClient, manager_auth_headers):
    """Test creating a cash payment (manager only)."""
    response = await async_client.post(
        "/api/v1/payment/cash",
        headers=manager_auth_headers,
        json={
            "amount": 5000,  # 50 ILS
            "tagIds": [],
            "notes": "Cash payment test",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_cash_payment_unauthorized(async_client: AsyncClient, auth_headers):
    """Test that regular users cannot create cash payments."""
    response = await async_client.post(
        "/api/v1/payment/cash",
        headers=auth_headers,
        json={
            "amount": 5000,
            "tagIds": [],
        },
    )

    assert response.status_code == 403  # Forbidden
