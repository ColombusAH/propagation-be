import pytest
from httpx import AsyncClient
from app.core.security import create_access_token
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

# Mock helper to create auth headers
def create_auth_headers(role: str, user_id: str = "test-user-id", business_id: str = "test-bus-id"):
    token = create_access_token(
        data={"sub": f"{role.lower()}@example.com", "user_id": user_id, "role": role, "business_id": business_id}
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_rbac_user_creation_flow(async_client: AsyncClient):
    """
    Test the hierarchical user creation flow:
    Super Admin -> Store Manager -> Employee -> Customer
    And verify forbidden actions.
    """
    
    # We need to mock get_user_by_id so that get_current_user returns a user with the correct role
    # instead of the default 'CUSTOMER' from conftest.py
    
    async def mock_get_user_by_id(db, user_id):
        # Return a user object based on the user_id hint (we'll encode role in ID for simplicity)
        role = "CUSTOMER"
        if "super_admin" in user_id:
            role = "SUPER_ADMIN"
        elif "store_manager" in user_id:
            role = "STORE_MANAGER"
        elif "network_manager" in user_id:
            role = "NETWORK_MANAGER"
        elif "employee" in user_id:
            role = "EMPLOYEE"
            
        return SimpleNamespace(
            id=user_id,
            email=f"{role.lower()}@example.com",
            role=role,
            businessId="test-bus-id",
            is_active=True
        )

    with patch("app.api.dependencies.auth.get_user_by_id", side_effect=mock_get_user_by_id):

        # Test: Store Manager trying to create Network Manager (Should Fail)
        store_manager_headers = create_auth_headers("STORE_MANAGER", user_id="store_manager_1")
        forbidden_request_data = {
            "email": "forbidden@example.com",
            "password": "password123", # valid length
            "name": "Should Fail",
            "role": "NETWORK_MANAGER",
            "phone": "0000000000",
            "address": "Nowhere",
            "businessId": "test-bus-id"
        }

        response = await async_client.post(
            "/api/v1/users/",
            json=forbidden_request_data,
            headers=store_manager_headers
        )
        assert response.status_code == 403, f"Expected 403 but got {response.status_code}. Body: {response.text}"
        assert "Not authorized to create users with role NETWORK_MANAGER" in response.json()["detail"]

        # Test: Store Manager trying to create Employee (Should Allow)
        employee_request_data = {
            "email": "employee@example.com",
            "password": "password123",
            "name": "Valid Employee",
            "role": "EMPLOYEE",
            "phone": "0000000000",
            "address": "Workplace",
            "businessId": "test-bus-id"
        }
        
        # We also need to mock create_user to avoid DB constraint errors since we don't have a real DB
        with patch("app.api.v1.endpoints.users.create_user", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = SimpleNamespace(
                id="new-emp-1",
                email="employee@example.com",
                role="EMPLOYEE",
                name="Valid Employee",
                phone="000",
                address="Addr",
                businessId="test-bus-id",
                createdAt="2023-01-01"
            )
            
            response = await async_client.post(
                "/api/v1/users/",
                json=employee_request_data,
                headers=store_manager_headers
            )
            assert response.status_code == 201, f"Expected 201 but got {response.status_code}. Body: {response.text}"

@pytest.mark.asyncio
async def test_endpoint_protection_decorator(async_client: AsyncClient):
    """Test standard endpoints protected by RBAC."""
    
    async def mock_get_user_by_id(db, user_id):
        role = "EMPLOYEE" # Default for this test
        return SimpleNamespace(
            id=user_id,
            email=f"{role.lower()}@example.com",
            role=role,
            businessId="test-bus-id",
            is_active=True
        )

    with patch("app.api.dependencies.auth.get_user_by_id", side_effect=mock_get_user_by_id):
        employee_headers = create_auth_headers("EMPLOYEE", user_id="employee_1")
        
        # Employee try to create user (Should Fail)
        response = await async_client.post(
            "/api/v1/users/",
            json={
                "email": "a@a.com", 
                "password": "password123", 
                "role": "CUSTOMER", 
                "name": "n", 
                "phone": "123", 
                "address": "addr", 
                "businessId": "b"
            },
            headers=employee_headers
        )
        assert response.status_code == 403
        assert "Not authorized to create users" in response.json()["detail"]
