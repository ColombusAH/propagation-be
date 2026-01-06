"""Unit tests for tag encryption service."""

import pytest

from app.services.tag_encryption import TagEncryptionService, get_encryption_service


@pytest.mark.unit
class TestTagEncryptionService:
    """Tests for TagEncryptionService class."""

    def test_service_initialization(self):
        """Test service initializes with a secret key."""
        service = TagEncryptionService(secret_key="test-secret-key-123")
        assert service.secret_key == "test-secret-key-123"
        assert service._fernet is not None

    def test_encrypt_tag_returns_string(self):
        """Test that encrypt_tag returns an encrypted string."""
        service = TagEncryptionService(secret_key="test-key")
        epc = "E2806810000000001234"

        encrypted = service.encrypt_tag(epc)

        assert encrypted is not None
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
        assert encrypted != epc  # Should be different from input

    def test_decrypt_qr_returns_original_epc(self):
        """Test that decrypt_qr returns the original EPC."""
        service = TagEncryptionService(secret_key="test-key")
        original_epc = "E2806810000000001234"

        encrypted = service.encrypt_tag(original_epc)
        decrypted = service.decrypt_qr(encrypted)

        assert decrypted == original_epc

    def test_verify_match_returns_true_for_matching(self):
        """Test verify_match returns True for matching EPC and QR."""
        service = TagEncryptionService(secret_key="test-key")
        epc = "E280681000ABCDEF5678"

        qr_code = service.encrypt_tag(epc)
        result = service.verify_match(epc, qr_code)

        assert result is True

    def test_verify_match_returns_false_for_non_matching(self):
        """Test verify_match returns False for non-matching EPC and QR."""
        service = TagEncryptionService(secret_key="test-key")
        epc1 = "E280681000ABCDEF5678"
        epc2 = "E280681000DIFFERENT"

        qr_code = service.encrypt_tag(epc1)
        result = service.verify_match(epc2, qr_code)

        assert result is False

    def test_verify_match_case_insensitive(self):
        """Test that EPC matching is case-insensitive."""
        service = TagEncryptionService(secret_key="test-key")
        epc_upper = "E280681000ABCDEF"
        epc_lower = "e280681000abcdef"

        qr_code = service.encrypt_tag(epc_upper)
        result = service.verify_match(epc_lower, qr_code)

        assert result is True

    def test_generate_hash_consistent(self):
        """Test that generate_hash produces consistent hashes."""
        service = TagEncryptionService(secret_key="test-key")
        epc = "E2806810000000001234"

        hash1 = service.generate_hash(epc)
        hash2 = service.generate_hash(epc)

        assert hash1 == hash2
        assert len(hash1) == 32  # SHA256 truncated to 32 chars

    def test_generate_hash_different_for_different_epcs(self):
        """Test that different EPCs produce different hashes."""
        service = TagEncryptionService(secret_key="test-key")
        epc1 = "E2806810000000001234"
        epc2 = "E2806810000000005678"

        hash1 = service.generate_hash(epc1)
        hash2 = service.generate_hash(epc2)

        assert hash1 != hash2

    def test_decrypt_invalid_qr_returns_none(self):
        """Test that decrypting invalid QR returns None."""
        service = TagEncryptionService(secret_key="test-key")

        result = service.decrypt_qr("invalid_qr_code")

        assert result is None

    def test_get_encryption_service_singleton(self):
        """Test get_encryption_service returns singleton instance."""
        service1 = get_encryption_service()
        service2 = get_encryption_service()

        assert service1 is service2
