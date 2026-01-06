"""
Encryption service for UHF Tag ↔ QR Code mapping.

The QR code and UHF tag will look different externally,
but the software can decrypt and compare them.

Uses AES encryption with a secret key stored in environment variables.
"""

import base64
import hashlib
import logging
import os
import secrets
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class TagEncryptionService:
    """Service for encrypting UHF tags and generating secure QR codes."""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize encryption service.

        Args:
            secret_key: Secret key for encryption. If not provided,
                       reads from TAG_ENCRYPTION_KEY environment variable.
        """
        self.secret_key = secret_key or os.getenv("TAG_ENCRYPTION_KEY")
        if not self.secret_key:
            # Generate a random key if not configured (development only)
            logger.warning("No TAG_ENCRYPTION_KEY set, generating random key")
            self.secret_key = secrets.token_urlsafe(32)

        self._fernet = self._create_fernet()

    def _create_fernet(self) -> Fernet:
        """Create a Fernet cipher from the secret key."""
        # Derive a proper key from the secret using PBKDF2
        salt = b"tagid_rf_salt_v1"  # Static salt, can be made dynamic
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return Fernet(key)

    def encrypt_tag(self, epc: str) -> str:
        """
        Encrypt an EPC tag value to create a QR-safe string.

        Args:
            epc: The UHF tag EPC value (e.g., "E2806810000000001234")

        Returns:
            Encrypted string safe for QR code generation
        """
        # Add a timestamp/nonce for uniqueness
        plaintext = f"TAG:{epc}:{secrets.token_hex(4)}"
        encrypted = self._fernet.encrypt(plaintext.encode())

        # Make it URL/QR safe - shorter than base64
        qr_code = base64.urlsafe_b64encode(encrypted).decode()

        logger.debug(f"Encrypted EPC {epc[:8]}... to QR code")
        return qr_code

    def decrypt_qr(self, qr_code: str) -> Optional[str]:
        """
        Decrypt a QR code back to the original EPC.

        Args:
            qr_code: The encrypted QR code string

        Returns:
            Original EPC value, or None if decryption fails
        """
        try:
            encrypted = base64.urlsafe_b64decode(qr_code.encode())
            decrypted = self._fernet.decrypt(encrypted).decode()

            # Parse the format: "TAG:EPC:nonce"
            parts = decrypted.split(":")
            if len(parts) >= 2 and parts[0] == "TAG":
                return parts[1]

            logger.warning(f"Invalid decrypted format: {decrypted[:20]}...")
            return None

        except Exception as e:
            logger.error(f"Failed to decrypt QR code: {e}")
            return None

    def verify_match(self, epc: str, qr_code: str) -> bool:
        """
        Verify if an EPC tag matches a QR code.

        Args:
            epc: The scanned UHF tag EPC
            qr_code: The scanned QR code

        Returns:
            True if they match (represent the same item)
        """
        decrypted_epc = self.decrypt_qr(qr_code)
        if decrypted_epc is None:
            return False

        return decrypted_epc.upper() == epc.upper()

    def generate_hash(self, epc: str) -> str:
        """
        Generate a one-way hash of an EPC for lookup purposes.

        This can be used as a "masked" EPC that can be compared
        without revealing the original.

        Args:
            epc: The UHF tag EPC value

        Returns:
            SHA-256 hash of the EPC with salt
        """
        salted = f"{self.secret_key}:{epc}:tagid"
        return hashlib.sha256(salted.encode()).hexdigest()[:32]


# Singleton instance
_encryption_service: Optional[TagEncryptionService] = None


def get_encryption_service() -> TagEncryptionService:
    """Get the singleton encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = TagEncryptionService()
    return _encryption_service
