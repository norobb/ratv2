"""
Client Security Module - Handles encryption and security for client
"""

import base64
import hashlib
import secrets
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ClientSecurity:
    """Client-side security management"""

    def __init__(self):
        self._fernet = None
        self._server_public_key = None
        self._session_key = None
        self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize encryption components"""
        # Generate session key for symmetric encryption
        self._session_key = secrets.token_bytes(32)

        # Initialize Fernet with session key
        key = base64.urlsafe_b64encode(self._session_key)
        self._fernet = Fernet(key)

    def set_server_public_key(self, public_key_pem: str):
        """Set server's RSA public key for key exchange"""
        self._server_public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )

    def encrypt_session_key(self) -> bytes:
        """Encrypt session key with server's public key"""
        if not self._server_public_key:
            raise ValueError("Server public key not set")

        return self._server_public_key.encrypt(
            self._session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt_message(self, message: str) -> str:
        """Encrypt message using session key"""
        if not self._fernet:
            raise ValueError("Encryption not initialized")

        encrypted = self._fernet.encrypt(message.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_message(self, encrypted_message: str) -> str:
        """Decrypt message using session key"""
        if not self._fernet:
            raise ValueError("Encryption not initialized")

        encrypted_data = base64.b64decode(encrypted_message.encode('utf-8'))
        decrypted = self._fernet.decrypt(encrypted_data)
        return decrypted.decode('utf-8')

    def generate_client_fingerprint(self) -> str:
        """Generate unique client fingerprint"""
        import platform
        import uuid

        # Collect system information
        system_info = {
            'platform': platform.system(),
            'processor': platform.processor(),
            'machine': platform.machine(),
            'node': platform.node(),
            'mac_address': hex(uuid.getnode())
        }

        # Create fingerprint hash
        fingerprint_data = ''.join(str(v) for v in system_info.values())
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()

    def secure_delete_key(self):
        """Securely delete encryption keys from memory"""
        if self._session_key:
            # Overwrite key with random data
            self._session_key = secrets.token_bytes(len(self._session_key))
            self._session_key = None

        self._fernet = None
