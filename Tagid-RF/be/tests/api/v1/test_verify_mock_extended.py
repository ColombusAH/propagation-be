"""
Coverage tests for Verification API endpoints.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.main import app


class TestVerifyEndpointCoverage:

    @pytest.mark.asyncio
    async def test_verify_product_not_found(self, client):
        with patch("app.api.v1.endpoints.verify.prisma_client") as mock_prisma:
            mock_db = MagicMock()
            mock_prisma.client.__aenter__ = AsyncMock(return_value=mock_db)
            mock_prisma.client.__aexit__ = AsyncMock()
            mock_db.rfidtag.find_unique = AsyncMock(return_value=None)

            response = await client.get("/api/v1/products/verify/MISSING")
            assert response.status_code == 200
            assert response.json()["is_authentic"] is False

    @pytest.mark.asyncio
    async def test_verify_product_stolen(self, client):
        with patch("app.api.v1.endpoints.verify.prisma_client") as mock_prisma:
            mock_db = MagicMock()
            mock_prisma.client.__aenter__ = AsyncMock(return_value=mock_db)
            mock_prisma.client.__aexit__ = AsyncMock()
            mock_db.rfidtag.find_unique = AsyncMock(
                return_value=SimpleNamespace(
                    epc="STOLEN1", status="STOLEN", productDescription="Phone"
                )
            )

            response = await client.get("/api/v1/products/verify/STOLEN1")
            assert response.status_code == 200
            assert response.json()["is_authentic"] is False
            assert "גנוב" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_verify_product_error(self, client):
        with patch("app.api.v1.endpoints.verify.prisma_client") as mock_prisma:
            mock_prisma.client.__aenter__ = AsyncMock(side_effect=Exception("DB Error"))
            mock_prisma.client.__aexit__ = AsyncMock()
            response = await client.get("/api/v1/products/verify/ERR")
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_verify_by_qr_success(self, client):
        with (
            patch("app.services.tag_encryption.get_encryption_service") as mock_get_svc,
            patch("app.api.v1.endpoints.verify.prisma_client") as mock_prisma,
        ):
            mock_svc = MagicMock()
            mock_get_svc.return_value = mock_svc
            mock_svc.decrypt_qr.return_value = "VALID_EPC"

            mock_db = MagicMock()
            mock_prisma.client.__aenter__ = AsyncMock(return_value=mock_db)
            mock_prisma.client.__aexit__ = AsyncMock()
            mock_db.rfidtag.find_unique = AsyncMock(
                return_value=SimpleNamespace(
                    epc="VALID_EPC", status="ACTIVE", productDescription="OK"
                )
            )

            response = await client.get("/api/v1/products/scan/SOME_QR")
            assert response.status_code == 200
            assert response.json()["is_authentic"] is True

    @pytest.mark.asyncio
    async def test_verify_by_qr_invalid(self, client):
        with patch("app.services.tag_encryption.get_encryption_service") as mock_get_svc:
            mock_svc = MagicMock()
            mock_get_svc.return_value = mock_svc
            mock_svc.decrypt_qr.side_effect = Exception("Decrypt Error")

            response = await client.get("/api/v1/products/scan/BAD_QR")
            assert response.status_code == 200
            assert response.json()["is_authentic"] is False
            assert "לא תקין" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_verify_by_qr_outer_error(self, client):
        with patch("app.services.tag_encryption.get_encryption_service") as mock_get_svc:
            mock_get_svc.side_effect = Exception("Service Error")
            response = await client.get("/api/v1/products/scan/ERR")
            assert response.status_code == 500
