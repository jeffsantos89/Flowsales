import os
import base64
import logging
from typing import Union, Optional
from functools import lru_cache
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class EncryptionError(Exception):
    """Exceção customizada para erros de criptografia"""
    pass

class SecretsManager:
    def __init__(self, salt: bytes = None):
        """
        Inicializa o gerenciador de segredos com uma chave de criptografia.
        
        Args:
            salt: Salt opcional para derivação da chave
        """
        self._salt = salt or os.urandom(16)
        self._cipher = self._initialize_cipher()
        
    @lru_cache(maxsize=1)
    def _initialize_cipher(self) -> Fernet:
        """
        Inicializa o cipher Fernet com derivação segura da chave.
        
        Returns:
            Fernet: Instância do cipher
        """
        try:
            secret_key = os.getenv("ENCRYPTION_KEY")
            if not secret_key:
                raise EncryptionError("ENCRYPTION_KEY environment variable is not set")

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self._salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
            return Fernet(key)
            
        except Exception as e:
            logger.error(f"Failed to initialize cipher: {str(e)}")
            raise EncryptionError(f"Cipher initialization failed: {str(e)}")

    def encrypt(self, data: Union[str, bytes], encoding: str = 'utf-8') -> str:
        """
        Encripta dados com o cipher Fernet.
        
        Args:
            data: Dados para encriptar (string ou bytes)
            encoding: Encoding para strings
            
        Returns:
            str: Dados encriptados em base64
        """
        try:
            if isinstance(data, str):
                data = data.encode(encoding)
            encrypted = self._cipher.encrypt(data)
            return base64.urlsafe_b64encode(encrypted).decode(encoding)
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError(f"Failed to encrypt data: {str(e)}")

    def decrypt(self, data: Union[str, bytes], encoding: str = 'utf-8') -> str:
        """
        Decripta dados encriptados com Fernet.
        
        Args:
            data: Dados encriptados para decriptar
            encoding: Encoding para strings
            
        Returns:
            str: Dados decriptados
        """
        try:
            if isinstance(data, str):
                data = base64.urlsafe_b64decode(data.encode(encoding))
            decrypted = self._cipher.decrypt(data)
            return decrypted.decode(encoding)
            
        except InvalidToken:
            logger.error("Invalid token or corrupted data")
            raise EncryptionError("Invalid token or corrupted data")
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError(f"Failed to decrypt data: {str(e)}")

    @property
    def salt(self) -> bytes:
        """Retorna o salt atual usado na derivação da chave"""
        return self._salt

# Singleton instance
@lru_cache(maxsize=1)
def get_secrets_manager() -> SecretsManager:
    """
    Retorna uma instância única do SecretsManager.
    
    Returns:
        SecretsManager: Instância singleton
    """
    return SecretsManager()

# Default instance
secrets_manager = get_secrets_manager()
