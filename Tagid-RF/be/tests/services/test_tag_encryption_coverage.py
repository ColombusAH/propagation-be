"""
Comprehensive tests for TagEncryptionService.
Covers: __init__, _create_fernet, encrypt_tag, decrypt_qr, verify_match, generate_hash, get_encryption_service
"""

import pytest
from unittest.mock import patch
import os


class TestTagEncryptionService:
    """Tests for TagEncryptionService."""

    @pytest.fixture
    def service(self):
        """Create TagEncryptionService with test key."""
        from app.services.tag_encryption import TagEncryptionService

        return TagEncryptionService(secret_key="test_secret_key_12345")

    def test_init_with_secret_key(self, service):
        """Test initialization with provided secret key."""
        assert service.secret_key == "test_secret_key_12345"
        assert service._fernet is not None

    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        with patch.dict(os.environ, {"TAG_ENCRYPTION_KEY": "env_key_12345"}):
            from app.services.tag_encryption import TagEncryptionService

            svc = TagEncryptionService()
            assert svc.secret_key == "env_key_12345"

    def test_init_generates_random_key(self):
        """Test initialization generates random key when none provided."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("app.services.tag_encryption.os.getenv", return_value=None):
                from app.services.tag_encryption import TagEncryptionService

                svc = TagEncryptionService()
                assert svc.secret_key is not None
                assert len(svc.secret_key) > 10

    def test_encrypt_tag(self, service):
        """Test encrypting an EPC tag."""
        epc = "E280681000001234"
        encrypted = service.encrypt_tag(epc)

        assert encrypted is not None
        assert encrypted != epc
        assert len(encrypted) > len(epc)

    def test_encrypt_tag_different_each_time(self, service):
        """Test that encryption produces unique results (due to nonce)."""
        epc = "E280681000001234"
        encrypted1 = service.encrypt_tag(epc)
        encrypted2 = service.encrypt_tag(epc)

        # Should be different due to random nonce
        assert encrypted1 != encrypted2

    def test_decrypt_qr_success(self, service):
        """Test successful QR decryption."""
        epc = "E280681000001234"
        encrypted = service.encrypt_tag(epc)

        decrypted = service.decrypt_qr(encrypted)

        assert decrypted == epc

    def test_decrypt_qr_invalid(self, service):
        """Test decryption of invalid QR code."""
        result = service.decrypt_qr("invalid_qr_code")
        assert result is None

    def test_decrypt_qr_wrong_key(self, service):
        """Test decryption with wrong key."""
        from app.services.tag_encryption import TagEncryptionService

        other_service = TagEncryptionService(secret_key="different_key_12345")

        encrypted = service.encrypt_tag("E280681000001234")
        result = other_service.decrypt_qr(encrypted)

        assert result is None

    def test_verify_match_true(self, service):
        """Test verify_match returns True for matching EPC and QR."""
        epc = "E280681000001234"
        encrypted = service.encrypt_tag(epc)

        result = service.verify_match(epc, encrypted)

        assert result is True

    def test_verify_match_false(self, service):
        """Test verify_match returns False for non-matching."""
        epc1 = "E280681000001234"
        epc2 = "E280681000005678"
        encrypted = service.encrypt_tag(epc1)

        result = service.verify_match(epc2, encrypted)

        assert result is False

    def test_verify_match_case_insensitive(self, service):
        """Test verify_match is case insensitive."""
        epc = "e280681000001234"  # lowercase
        encrypted = service.encrypt_tag("E280681000001234")  # uppercase

        result = service.verify_match(epc, encrypted)

        assert result is True

    def test_verify_match_invalid_qr(self, service):
        """Test verify_match with invalid QR code."""
        result = service.verify_match("E280681000001234", "invalid")
        assert result is False

    def test_generate_hash(self, service):
        """Test generating hash of EPC."""
        epc = "E280681000001234"
        hash1 = service.generate_hash(epc)

        assert hash1 is not None
        assert len(hash1) == 32  # SHA-256 truncated to 32 chars

    def test_generate_hash_consistent(self, service):
        """Test hash is consistent for same input."""
        epc = "E280681000001234"
        hash1 = service.generate_hash(epc)
        hash2 = service.generate_hash(epc)

        assert hash1 == hash2

    def test_generate_hash_different_for_different_epc(self, service):
        """Test hash is different for different EPCs."""
        hash1 = service.generate_hash("E280681000001234")
        hash2 = service.generate_hash("E280681000005678")

        assert hash1 != hash2


class TestGetEncryptionService:
    """Tests for get_encryption_service singleton."""

    def test_get_encryption_service_singleton(self):
        """Test that get_encryption_service returns singleton."""
        # Clear the singleton first
        import app.services.tag_encryption as module

        module._encryption_service = None

        from app.services.tag_encryption import get_encryption_service

        service1 = get_encryption_service()
        service2 = get_encryption_service()

        assert service1 is service2
