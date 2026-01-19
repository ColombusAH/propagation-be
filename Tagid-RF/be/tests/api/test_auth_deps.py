from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from app.api.dependencies.auth import get_current_user
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from prisma.models import User


@pytest.mark.asyncio
async def test_get_current_user_no_token():
    with pytest.raises(HTTPException) as exc:
        await get_current_user(authorization=None, db=MagicMock())
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    mock_auth = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")
    with patch("app.api.dependencies.auth.verify_access_token") as mock_verify:
        mock_verify.return_value = None
        with pytest.raises(HTTPException) as exc:
            await get_current_user(authorization=mock_auth, db=MagicMock())
        assert exc.value.status_code == 401
