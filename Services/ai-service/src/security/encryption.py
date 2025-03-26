from cryptography.fernet import Fernet, InvalidToken
from typing import Union, Optional
import base64
import logging
from functools import wraps
import secrets
from config.settings import settings

logger = logging.getLogger(__name__)

class EncryptionError(Exception):
    """Custom exception for encryption related errors"""
    pass

class Encryptor:
    def __init__(self, key: Union[str, bytes]):
        try:
            if isinstance(key, str):
                key = key.encode()
            self.cipher = Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize Fernet cipher: {str(e)}")
            raise EncryptionError("Invalid encryption key")

    @staticmethod
    def generate_key() -> bytes:
        """Generate a secure encryption key"""
        try:
            return Fernet.generate_key()
        except Exception as e:
            logger.error(f"Failed to generate key: {str(e)}")
            raise EncryptionError("Failed to generate encryption key")

    def encrypt_data(self, data: Union[str, bytes], ttl: Optional[int] = None) -> str:
        """
        Encrypt data with optional time-to-live in seconds
        Returns base64 encoded encrypted string
        """
        try:
            if isinstance(data, str):
                data = data.encode()
            
            encrypted = self.cipher.encrypt(data) if ttl is None else self.cipher.encrypt_at_time(data, ttl)
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError("Failed to encrypt data")

    def decrypt_data(self, encrypted_data: str, ttl_check: bool = True) -> str:
        """
        Decrypt base64 encoded encrypted string
        ttl_check: whether to verify time-to-live
        """
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted) if not ttl_check else self.cipher.decrypt_at_time(encrypted)
            return decrypted.decode('utf-8')
        except InvalidToken:
            logger.error("Invalid token or expired TTL")
            raise EncryptionError("Invalid or expired encrypted data")
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError("Failed to decrypt data")

def require_encryption(func):
    """Decorator to ensure encryption is properly initialized"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(encryptor, 'cipher'):
            raise EncryptionError("Encryption not initialized")
        return func(*args, **kwargs)
    return wrapper

# Initialize global encryptor instance
try:
    encryptor = Encryptor(settings.ENCRYPTION_KEY)
except EncryptionError as e:
    logger.critical(f"Failed to initialize encryption: {str(e)}")
    raise

# Convenience functions
@require_encryption
def encrypt_data(data: str, ttl: Optional[int] = None) -> str:
    return encryptor.encrypt_data(data, ttl)

@require_encryption
def decrypt_data(encrypted_data: str, ttl_check: bool = True) -> str:
    return encryptor.decrypt_data(encrypted_data, ttl_check)

@require_encryption
def rotate_key() -> bytes:
    """Generate new key and re-encrypt all necessary data"""
    new_key = Encryptor.generate_key()
    # Implement key rotation logic here
    return new_key
