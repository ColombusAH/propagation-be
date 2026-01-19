from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.core.permissions import (can_create_role, is_admin, is_manager,
                                  requires_any_role, requires_role)
from fastapi import HTTPException, status
from prisma.models import User


def create_mock_user(role: str):
    user = MagicMock(spec=User)
    user.role = role
    return user


class TestPermissions:

    def test_is_admin(self):
        assert is_admin(create_mock_user("SUPER_ADMIN")) is True
        assert is_admin(create_mock_user("NETWORK_MANAGER")) is True
        assert is_admin(create_mock_user("STORE_MANAGER")) is False
        assert is_admin(create_mock_user("CUSTOMER")) is False

    def test_is_manager(self):
        assert is_manager(create_mock_user("SUPER_ADMIN")) is True
        assert is_manager(create_mock_user("NETWORK_MANAGER")) is True
        assert is_manager(create_mock_user("STORE_MANAGER")) is True
        assert is_manager(create_mock_user("EMPLOYEE")) is False
        assert is_manager(create_mock_user("CUSTOMER")) is False

    def test_can_create_role(self):
        # SUPER_ADMIN can create anything
        admin = create_mock_user("SUPER_ADMIN")
        assert can_create_role(admin, "SUPER_ADMIN") is True
        assert can_create_role(admin, "CUSTOMER") is True

        # NETWORK_MANAGER hierarchy
        nm = create_mock_user("NETWORK_MANAGER")
        assert can_create_role(nm, "SUPER_ADMIN") is False
        assert can_create_role(nm, "STORE_MANAGER") is True
        assert can_create_role(nm, "CUSTOMER") is True

        # STORE_MANAGER hierarchy
        sm = create_mock_user("STORE_MANAGER")
        assert can_create_role(sm, "NETWORK_MANAGER") is False
        assert can_create_role(sm, "EMPLOYEE") is True

        # Others can create nothing
        cust = create_mock_user("CUSTOMER")
        assert can_create_role(cust, "CUSTOMER") is False

    @pytest.mark.asyncio
    async def test_requires_role_decorator_success(self):
        # requires_role uses a decorator pattern
        @requires_role("ADMIN", "MANAGER")
        async def mock_endpoint(current_user: User):
            return "success"

        user = create_mock_user("ADMIN")
        result = await mock_endpoint(current_user=user)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_requires_role_decorator_forbidden(self):
        @requires_role("ADMIN")
        async def mock_endpoint(current_user: User):
            return "success"

        user = create_mock_user("CUSTOMER")
        with pytest.raises(HTTPException) as excinfo:
            await mock_endpoint(current_user=user)
        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_requires_any_role_dependency_success(self):
        # requires_any_role returns a dependency function
        check_role = requires_any_role(["ADMIN", "MANAGER"])
        user = create_mock_user("MANAGER")

        result = await check_role(current_user=user)
        assert result == user  # Now returns the user object

    @pytest.mark.asyncio
    async def test_requires_any_role_dependency_forbidden(self):
        check_role = requires_any_role(["ADMIN"])
        user = create_mock_user("CUSTOMER")

        with pytest.raises(HTTPException) as excinfo:
            await check_role(current_user=user)
        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
