"""
Tests for TagEncryptionService - Pure unit tests without external dependencies.
"""

import pytest

from app.services.tag_encryption import TagEncryptionService, get_encryption_service


@pytest.fixture
def encryption_service():
    # Use a fixed key for reproducible tests
    return TagEncryptionService(secret_key="test_secret_key_12345")


def test_encrypt_decrypt_roundtrip(encryption_service):
    """Test that encryption and decryption are reversible."""
    original_epc = "E2806810000000001234ABCD"

    encrypted = encryption_service.encrypt_tag(original_epc)
    decrypted = encryption_service.decrypt_qr(encrypted)

    assert decrypted == original_epc
    assert encrypted != original_epc  # Should be obfuscated


def test_encrypted_values_are_unique(encryption_service):
    """Each encryption should produce a unique result due to nonce."""
    epc = "E2806810000000001234ABCD"

    encrypted1 = encryption_service.encrypt_tag(epc)
    encrypted2 = encryption_service.encrypt_tag(epc)

    # Same EPC but different ciphertexts (due to random nonce)
    assert encrypted1 != encrypted2

    # Both should decrypt to the same EPC
    assert encryption_service.decrypt_qr(encrypted1) == epc
    assert encryption_service.decrypt_qr(encrypted2) == epc


def test_verify_match_success(encryption_service):
    """Test successful verification of matching EPC and QR."""
    epc = "E2806810000000005678EFGH"
    qr_code = encryption_service.encrypt_tag(epc)

    assert encryption_service.verify_match(epc, qr_code) is True


def test_verify_match_failure_wrong_epc(encryption_service):
    """Test verification fails with wrong EPC."""
    epc1 = "E2806810000000001111AAAA"
    epc2 = "E2806810000000002222BBBB"

    qr_code = encryption_service.encrypt_tag(epc1)

    assert encryption_service.verify_match(epc2, qr_code) is False


def test_verify_match_case_insensitive(encryption_service):
    """Verification should be case-insensitive."""
    epc_upper = "E2806810ABCD"
    epc_lower = "e2806810abcd"

    qr_code = encryption_service.encrypt_tag(epc_upper)

    assert encryption_service.verify_match(epc_lower, qr_code) is True


def test_decrypt_invalid_qr_returns_none(encryption_service):
    """Invalid QR codes should return None."""
    assert encryption_service.decrypt_qr("invalid_data") is None
    assert encryption_service.decrypt_qr("") is None


def test_generate_hash(encryption_service):
    """Test hash generation is consistent."""
    epc = "E2806810000000001234ABCD"

    hash1 = encryption_service.generate_hash(epc)
    hash2 = encryption_service.generate_hash(epc)

    assert hash1 == hash2
    assert len(hash1) == 32  # Truncated SHA256


def test_different_epc_different_hash(encryption_service):
    """Different EPCs should produce different hashes."""
    hash1 = encryption_service.generate_hash("EPC_ONE")
    hash2 = encryption_service.generate_hash("EPC_TWO")

    assert hash1 != hash2


def test_get_encryption_service_singleton():
    """Test singleton pattern."""
    svc1 = get_encryption_service()
    svc2 = get_encryption_service()

    assert svc1 is svc2


def test_service_init_without_key():
    """Service should generate random key if not provided."""
    # Temporarily remove env var if set
    import os

    original = os.environ.pop("TAG_ENCRYPTION_KEY", None)

    try:
        svc = TagEncryptionService()
        assert svc.secret_key is not None
        assert len(svc.secret_key) > 0
    finally:
        if original:
            os.environ["TAG_ENCRYPTION_KEY"] = original
