"""
Comprehensive tests for Auth API endpoints.
Covers: auth_root, dev_login, get_me, login_with_google, login_with_email, register_user
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestAuthRoot:
    """Tests for GET /auth/ endpoint."""

    @pytest.mark.asyncio
    async def test_auth_root(self, client):
        """Test auth root endpoint."""
        response = await client.get("/api/v1/auth/")
        assert response.status_code == 200
        assert "message" in response.json()


class TestDevLogin:
    """Tests for POST /auth/dev-login endpoint."""

    @pytest.mark.asyncio
    async def test_dev_login_store_manager(self, client):
        """Test dev login as STORE_MANAGER."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        mock_db_instance.business = MagicMock()
        mock_db_instance.business.find_first = AsyncMock(return_value=MagicMock(id="biz-1"))
        mock_db_instance.user = MagicMock()
        mock_db_instance.user.find_unique = AsyncMock(return_value=None)
        mock_db_instance.user.create = AsyncMock(return_value=MagicMock(
            id="user-1",
            email="dev_store_manager@example.com",
            role="STORE_MANAGER",
            businessId="biz-1"
        ))

        app.dependency_overrides[get_db] = lambda: mock_db_instance
        try:
            with patch("app.api.v1.endpoints.auth.get_user_by_email") as mock_get_user:
                mock_get_user.return_value = None # Force creation
                
                response = await client.post("/api/v1/auth/dev-login", json={"role": "STORE_MANAGER"})
                assert response.status_code == 200
                assert "access_token" in response.json()
        finally:
            app.dependency_overrides.clear()


    @pytest.mark.asyncio
    async def test_dev_login_admin(self, client):
        """Test dev login as ADMIN."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        mock_db_instance.business = MagicMock()
        mock_db_instance.business.find_first = AsyncMock(return_value=MagicMock(id="biz-1"))
        mock_db_instance.user = MagicMock()
        mock_db_instance.user.find_unique = AsyncMock(return_value=MagicMock(
            id="user-admin", email="dev_admin@example.com", role="SUPER_ADMIN", businessId="biz-1"
        ))
        
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        try:
            response = await client.post("/api/v1/auth/dev-login", json={"role": "ADMIN"})
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_dev_login_customer(self, client):
        """Test dev login as CUSTOMER."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        mock_db_instance.business = MagicMock()
        mock_db_instance.business.find_first = AsyncMock(return_value=MagicMock(id="biz-1"))
        mock_db_instance.user = MagicMock()
        mock_db_instance.user.find_unique = AsyncMock(return_value=MagicMock(
            id="user-customer", email="dev_customer@example.com", role="CUSTOMER", businessId="biz-1"
        ))
        
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        try:
            response = await client.post("/api/v1/auth/dev-login", json={"role": "CUSTOMER"})
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()


class TestGetMe:
    """Tests for GET /auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client):
        """Test get_me without authentication."""
        # Ensure no overrides
        from app.api.dependencies.auth import get_current_user
        from app.main import app
        
        async def fail_auth():
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Unauthenticated")
            
        app.dependency_overrides[get_current_user] = fail_auth
        try:
            response = await client.get("/api/v1/auth/me")
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client):
        """Test get_me with authentication (mocked)."""
        from app.api.dependencies.auth import get_current_user
        from app.main import app
        
        mock_user = MagicMock()
        mock_user.id = "user-1"
        mock_user.email = "test@example.com"
        
        app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            response = await client.get("/api/v1/auth/me")
            assert response.status_code == 200
            assert response.json()["email"] == "test@example.com"
        finally:
            app.dependency_overrides.clear()


class TestLoginWithGoogle:
    """Tests for POST /auth/google endpoint."""

    @pytest.mark.asyncio
    async def test_login_with_google_invalid_token(self, client):
        """Test Google login with invalid token."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        
        try:
            with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify:
                mock_verify.side_effect = ValueError("Invalid token")
                response = await client.post("/api/v1/auth/google", json={"token": "invalid_token"})
                assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_with_google_valid_token_user_not_found(self, client):
        """Test Google login with valid token but user not in DB."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        
        try:
            with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify, \
                 patch("app.api.v1.endpoints.auth.get_user_by_email") as mock_get_user:
                
                mock_verify.return_value = {
                    "email": "test@example.com",
                    "sub": "google-sub-123"
                }
                mock_get_user.return_value = None

                response = await client.post("/api/v1/auth/google", json={"token": "valid_google_token"})
                assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()


    @pytest.mark.asyncio
    async def test_login_with_google_success(self, client):
        """Test successful Google login."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        mock_db_instance.user = MagicMock()
        mock_db_instance.user.update = AsyncMock()
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        
        try:
            with patch("app.api.v1.endpoints.auth.id_token.verify_oauth2_token") as mock_verify, \
                 patch("app.api.v1.endpoints.auth.get_user_by_email") as mock_get_user, \
                 patch("app.api.v1.endpoints.auth.update_user_google_info") as mock_update:

                mock_verify.return_value = {
                    "email": "test@example.com",
                    "sub": "google-sub-123"
                }
                mock_get_user.return_value = MagicMock(
                    id="user-1",
                    email="test@example.com",
                    role="CUSTOMER",
                    subId=None,
                    businessId="biz-1"
                )
                mock_update.return_value = None

                response = await client.post("/api/v1/auth/google", json={"token": "valid_google_token"})
                assert response.status_code == 200
                assert "access_token" in response.json()
        finally:
            app.dependency_overrides.clear()


    @pytest.mark.asyncio
    async def test_login_with_google_no_client_id(self, client):
        """Test Google login when GOOGLE_CLIENT_ID is not configured."""
        with patch("app.api.v1.endpoints.auth.GOOGLE_CLIENT_ID", None):
            response = await client.post("/api/v1/auth/google", json={"token": "some_token"})
            assert response.status_code == 500


class TestLoginWithEmail:
    """Tests for POST /auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_with_email_invalid_credentials(self, client):
        """Test email login with invalid credentials."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        try:
            with patch("app.api.v1.endpoints.auth.authenticate_user") as mock_auth:
                mock_auth.return_value = None
                response = await client.post("/api/v1/auth/login", json={
                    "email": "wrong@example.com",
                    "password": "wrongpassword"
                })
                assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_with_email_success(self, client):
        """Test successful email login."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        
        try:
            with patch("app.api.v1.endpoints.auth.authenticate_user") as mock_auth:
                mock_auth.return_value = MagicMock(
                    id="user-1",
                    email="test@example.com",
                    role="CUSTOMER",
                    businessId="biz-1"
                )

                response = await client.post("/api/v1/auth/login", json={
                    "email": "test@example.com",
                    "password": "correctpassword"
                })
                assert response.status_code == 200
                assert "access_token" in response.json()
        finally:
            app.dependency_overrides.clear()


    @pytest.mark.asyncio
    async def test_login_with_email_empty_password(self, client):
        """Test email login with empty password."""
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": ""
        })
        assert response.status_code in [401, 422]


class TestRegisterUser:
    """Tests for POST /auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_user_as_customer(self, client):
        """Test user registration as CUSTOMER."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        
        try:
            with patch("app.api.v1.endpoints.auth.get_user_by_email") as mock_get, \
                 patch("app.api.v1.endpoints.auth.create_user") as mock_create:
                
                mock_get.return_value = None
                mock_create.return_value = MagicMock(
                    id="new-user-1",
                    email="newuser@example.com",
                    role="CUSTOMER",
                    businessId=None
                )

                response = await client.post("/api/v1/auth/register", json={
                    "email": "newuser@example.com",
                    "password": "password123",
                    "name": "Test User",
                    "role": "CUSTOMER"
                })
                assert response.status_code == 201
        finally:
            app.dependency_overrides.clear()


    @pytest.mark.asyncio
    async def test_register_user_non_customer_role_rejected(self, client):
        """Test that non-CUSTOMER role registration is rejected."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "admin@example.com",
            "password": "password123",
            "name": "Admin User",
            "role": "STORE_MANAGER"
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, client):
        """Test registration with existing email."""
        from app.db.dependencies import get_db
        from app.main import app
        
        mock_db_instance = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db_instance
        try:
            with patch("app.api.v1.endpoints.auth.get_user_by_email") as mock_get:
                mock_get.return_value = MagicMock(id="existing-user")

                response = await client.post("/api/v1/auth/register", json={
                    "email": "existing@example.com",
                    "password": "password123",
                    "name": "Test User",
                    "role": "CUSTOMER"
                })
                assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com"
            # Missing password, name, role
        })
        assert response.status_code == 422

