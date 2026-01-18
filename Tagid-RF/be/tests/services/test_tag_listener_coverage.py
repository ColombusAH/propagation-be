import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.services.tag_listener_service import TagListenerService


@pytest.fixture
def service():
    return TagListenerService(port=9999)


@pytest.mark.asyncio
async def test_broadcast_tag_success_with_encryption(service):
    # Mock data
    tag_data = {
        "tag_id": "1",
        "epc": "E2000000001",
        "rssi": -60,
        "antenna_port": 1,
        "timestamp": datetime.now().isoformat(),
    }

    # Mock dependencies
    mock_db = MagicMock()
    mock_mapping = MagicMock()
    mock_mapping.encryptedQr = "encrypted_data"
    mock_db.tagmapping.find_unique = AsyncMock(return_value=mock_mapping)

    mock_tag_db = MagicMock()
    mock_tag_db.product_name = "Nike Shoe"
    mock_tag_db.product_sku = "SKU123"
    mock_tag_db.price_cents = 5000
    mock_tag_db.is_paid = True

    mock_encrypt_svc = MagicMock()
    mock_encrypt_svc.decrypt_qr.return_value = "decrypted_qr_link"

    # Patch the singleton wrapper directly
    with patch("app.db.prisma.prisma_client") as mock_p:
        mock_p.client.__aenter__.return_value = mock_db
        with patch("app.services.database.SessionLocal") as mock_session_cls:
            mock_session = mock_session_cls.return_value
            mock_session.query.return_value.filter.return_value.first.return_value = mock_tag_db

            with patch(
                "app.services.tag_encryption.get_encryption_service", return_value=mock_encrypt_svc
            ):
                with patch(
                    "app.services.tag_listener_service.manager.broadcast", new_callable=AsyncMock
                ) as mock_broadcast:

                    await service._broadcast_tag(tag_data)

                    mock_broadcast.assert_called()
                    call_args = mock_broadcast.call_args[0][0]
                    assert call_args["type"] == "tag_scanned"
                    assert call_args["data"]["product_name"] == "Nike Shoe"
                    assert call_args["data"]["decrypted_qr"] == "decrypted_qr_link"
                    assert call_args["data"]["is_encrypted"] is True


@pytest.mark.asyncio
async def test_broadcast_tag_theft_alert(service):
    tag_data = {"epc": "STOLEN123", "tag_id": "2"}

    mock_tag_db = MagicMock()
    mock_tag_db.product_name = "Luxury Watch"
    mock_tag_db.is_paid = False

    with patch("app.db.prisma.prisma_client") as mock_p:
        mock_p.client.__aenter__.return_value = MagicMock()
        with patch("app.services.database.SessionLocal") as mock_session_cls:
            mock_session = mock_session_cls.return_value
            mock_session.query.return_value.filter.return_value.first.return_value = mock_tag_db

            with patch(
                "app.services.tag_listener_service.manager.broadcast", new_callable=AsyncMock
            ) as mock_broadcast:
                await service._broadcast_tag(tag_data)

                assert mock_broadcast.call_count == 2
                types = [c.args[0]["type"] for c in mock_broadcast.call_args_list]
                assert "theft_alert" in types


@pytest.mark.asyncio
async def test_broadcast_tag_prisma_error(service):
    tag_data = {"epc": "ERROR_EPC"}

    with patch("app.db.prisma.prisma_client") as mock_p:
        mock_p.client.__aenter__.side_effect = Exception("Prisma Error")
        with patch("app.services.database.SessionLocal"):
            with patch(
                "app.services.tag_listener_service.manager.broadcast", new_callable=AsyncMock
            ) as mock_broadcast:
                await service._broadcast_tag(tag_data)
                mock_broadcast.assert_called()


@pytest.mark.asyncio
async def test_broadcast_tag_decryption_error(service):
    tag_data = {"epc": "BAD_QR"}

    mock_db = MagicMock()
    mock_mapping = MagicMock()
    mock_mapping.encryptedQr = "bad_data"
    mock_db.tagmapping.find_unique = AsyncMock(return_value=mock_mapping)

    mock_encrypt_svc = MagicMock()
    mock_encrypt_svc.decrypt_qr.side_effect = Exception("Decryption Error")

    with patch("app.db.prisma.prisma_client") as mock_p:
        mock_p.client.__aenter__.return_value = mock_db
        with patch(
            "app.services.tag_encryption.get_encryption_service", return_value=mock_encrypt_svc
        ):
            with patch(
                "app.services.tag_listener_service.manager.broadcast", new_callable=AsyncMock
            ) as mock_broadcast:
                await service._broadcast_tag(tag_data)

                call_args = mock_broadcast.call_args[0][0]
                assert call_args["data"]["decrypted_qr"] == "Decryption Failed"


def test_service_stats_and_recent(service):
    from app.services.tag_listener_service import tag_store

    tag_store.add_tag({"epc": "E1", "tag_id": "1"})

    stats = service.get_stats()
    assert stats["total_scans"] >= 1

    recent = service.get_recent_tags(count=1)
    assert len(recent) == 1


def test_on_tag_scanned_sync(service):
    tag_data = {"epc": "SYNC_EPC"}
    service._loop = MagicMock()
    service._loop.is_running.return_value = True

    callback = MagicMock()
    service.add_tag_callback(callback)

    with patch("asyncio.run_coroutine_threadsafe") as mock_run:
        service.on_tag_scanned_sync(tag_data)
        mock_run.assert_called_once()
        callback.assert_called_once_with(tag_data)


@pytest.mark.asyncio
async def test_start_stop_service(service):
    with patch("tag_listener_server.start_server"):
        with patch("threading.Thread"):
            service.start()
            assert service._running is True
            service.stop()
            assert service._running is False
