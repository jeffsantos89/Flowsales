from cryptography.fernet import Fernet
from typing import Optional
from pydantic import BaseSettings
import os
from functools import lru_cache

class SecuritySettings:
    JWT_SECRET = "super-secret-key"
    ENCRYPTION_KEY = b"my-encryption-key"
    OAUTH2_PROVIDER = "https://auth.example.com"
    ENABLE_MTLS = True

security_settings = SecuritySettings()
class SecuritySettings(BaseSettings):
    JWT_SECRET: str = os.getenv("JWT_SECRET", Fernet.generate_key().decode())
    ENCRYPTION_KEY: bytes = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
    OAUTH2_PROVIDER: str = os.getenv("OAUTH2_PROVIDER", "https://auth.example.com")
    ENABLE_MTLS: bool = os.getenv("ENABLE_MTLS", "True").lower() == "true"
    TOKEN_EXPIRATION: int = int(os.getenv("TOKEN_EXPIRATION", "3600"))
    ALGORITHM: str = "HS256"
    MIN_PASSWORD_LENGTH: int = 12
    REQUIRED_SPECIAL_CHARS: bool = True
    MAX_LOGIN_ATTEMPTS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_security_settings() -> SecuritySettings:
    return SecuritySettings()

security_settings = get_security_settings()