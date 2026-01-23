import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


def create_mock_user(id="user-1", email="test@example.com", role="CUSTOMER", business_id="biz-1"):
    """Helper to create a clean mock user that satisfies Prisma/Pydantic schemas."""
    return SimpleNamespace(
        id=id,
        email=email,
        name=f"Mock {role}",
        phone="000-000-0000",
        address="Mock Adr",
        role=role,
        businessId=business_id,
        subId=None,
        description=None,
        password="hashedpassword",
        verifiedBy=None,
        createdAt=datetime.datetime.now(),
        updatedAt=datetime.datetime.now(),
        deletedAt=None,
        latitude=None,
        longitude=None,
        receiveTheftAlerts=False,
        business=None,
        notifications=[],
        tags=[],
        availabilityPreferences=[],
        notificationPreferences=[],
        shiftAssignments=[],
        shiftResponses=[],
        requestedReplacements=[],
        providedReplacements=[],
        botConversations=[],
        formSubmissions=[],
        scheduleGenerationRequests=[],
        alertRecipients=[],
    )


@pytest.mark.asyncio
async def test_google_login_success(client: AsyncClient):
    """Test successful Google login with mocking."""
    from app.db.dependencies import get_db
    from app.main import app

    app.dependency_overrides[get_db] = lambda: MagicMock()
    try:
        payload = {"token": "mock-valid-token"}

        with (
            patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify,
            patch("app.api.v1.endpoints.auth.get_user_by_email") as mock_get_user,
        ):

            mock_verify.return_value = {
                "email": "test@example.com",
                "sub": "google-sub-123",
            }
            mock_user = create_mock_user(
                id="user-123",
                email="test@example.com",
                role="SUPER_ADMIN",
                business_id="biz-123",
            )
            mock_user.subId = "google-sub-123"
            mock_get_user.return_value = mock_user

            response = await client.post("/api/v1/auth/google", json=payload)
            assert response.status_code == 200
            assert "token" in response.json()
            assert response.json()["user_id"] == "user-123"
    finally:
        app.dependency_overrides.clear()
