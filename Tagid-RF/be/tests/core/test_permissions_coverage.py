"""
Comprehensive tests for permissions.py (RBAC utilities).
Covers: requires_role, requires_any_role, is_admin, is_manager, can_create_role
"""

import pytest
from unittest.mock import MagicMock, patch


class MockUser:
    """Mock User object for testing."""

    def __init__(self, role: str):
        self.role = role
        self.id = "user-123"
        self.email = "test@example.com"


class TestIsAdmin:
    """Tests for is_admin function."""

    def test_is_admin_super_admin(self):
        """Test SUPER_ADMIN is admin."""
        from app.core.permissions import is_admin

        user = MockUser("SUPER_ADMIN")
        assert is_admin(user) is True

    def test_is_admin_network_manager(self):
        """Test NETWORK_MANAGER is admin."""
        from app.core.permissions import is_admin

        user = MockUser("NETWORK_MANAGER")
        assert is_admin(user) is True

    def test_is_admin_store_manager(self):
        """Test STORE_MANAGER is not admin."""
        from app.core.permissions import is_admin

        user = MockUser("STORE_MANAGER")
        assert is_admin(user) is False

    def test_is_admin_employee(self):
        """Test EMPLOYEE is not admin."""
        from app.core.permissions import is_admin

        user = MockUser("EMPLOYEE")
        assert is_admin(user) is False


class TestIsManager:
    """Tests for is_manager function."""

    def test_is_manager_super_admin(self):
        """Test SUPER_ADMIN is manager."""
        from app.core.permissions import is_manager

        user = MockUser("SUPER_ADMIN")
        assert is_manager(user) is True

    def test_is_manager_network_manager(self):
        """Test NETWORK_MANAGER is manager."""
        from app.core.permissions import is_manager

        user = MockUser("NETWORK_MANAGER")
        assert is_manager(user) is True

    def test_is_manager_store_manager(self):
        """Test STORE_MANAGER is manager."""
        from app.core.permissions import is_manager

        user = MockUser("STORE_MANAGER")
        assert is_manager(user) is True

    def test_is_manager_employee(self):
        """Test EMPLOYEE is not manager."""
        from app.core.permissions import is_manager

        user = MockUser("EMPLOYEE")
        assert is_manager(user) is False

    def test_is_manager_customer(self):
        """Test CUSTOMER is not manager."""
        from app.core.permissions import is_manager

        user = MockUser("CUSTOMER")
        assert is_manager(user) is False


class TestCanCreateRole:
    """Tests for can_create_role function."""

    def test_super_admin_can_create_all(self):
        """Test SUPER_ADMIN can create all roles."""
        from app.core.permissions import can_create_role

        user = MockUser("SUPER_ADMIN")

        assert can_create_role(user, "SUPER_ADMIN") is True
        assert can_create_role(user, "NETWORK_MANAGER") is True
        assert can_create_role(user, "STORE_MANAGER") is True
        assert can_create_role(user, "EMPLOYEE") is True
        assert can_create_role(user, "CUSTOMER") is True

    def test_network_manager_permissions(self):
        """Test NETWORK_MANAGER role creation permissions."""
        from app.core.permissions import can_create_role

        user = MockUser("NETWORK_MANAGER")

        assert can_create_role(user, "SUPER_ADMIN") is False
        assert can_create_role(user, "NETWORK_MANAGER") is False
        assert can_create_role(user, "STORE_MANAGER") is True
        assert can_create_role(user, "EMPLOYEE") is True
        assert can_create_role(user, "CUSTOMER") is True

    def test_store_manager_permissions(self):
        """Test STORE_MANAGER role creation permissions."""
        from app.core.permissions import can_create_role

        user = MockUser("STORE_MANAGER")

        assert can_create_role(user, "SUPER_ADMIN") is False
        assert can_create_role(user, "NETWORK_MANAGER") is False
        assert can_create_role(user, "STORE_MANAGER") is False
        assert can_create_role(user, "EMPLOYEE") is True
        assert can_create_role(user, "CUSTOMER") is True

    def test_employee_no_permissions(self):
        """Test EMPLOYEE cannot create any roles."""
        from app.core.permissions import can_create_role

        user = MockUser("EMPLOYEE")

        assert can_create_role(user, "EMPLOYEE") is False
        assert can_create_role(user, "CUSTOMER") is False


class TestRequiresAnyRole:
    """Tests for requires_any_role dependency."""

    @pytest.mark.asyncio
    async def test_requires_any_role_allowed(self):
        """Test access with allowed role."""
        from app.core.permissions import requires_any_role

        check_role = requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER"])

        with patch("app.core.permissions.get_current_user") as mock_get_user:
            user = MockUser("SUPER_ADMIN")
            mock_get_user.return_value = user

            # The function returns the user if allowed
            result = await check_role(current_user=user)
            assert result == user

    @pytest.mark.asyncio
    async def test_requires_any_role_denied(self):
        """Test access denied for non-allowed role."""
        from app.core.permissions import requires_any_role
        from fastapi import HTTPException

        check_role = requires_any_role(["SUPER_ADMIN"])

        user = MockUser("EMPLOYEE")

        with pytest.raises(HTTPException) as exc:
            await check_role(current_user=user)

        assert exc.value.status_code == 403
