from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache
import os
from enum import Enum

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Application settings with validation and environment configuration."""
    
    # Application Info
    PROJECT_NAME: str = "AI Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    SECURITY_BCRYPT_ROUNDS: int = 12
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_TIMEOUT: int = 30
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def dict_with_sensitive_data_masked(self) -> dict:
        """Returns settings with sensitive data masked."""
        settings_dict = self.model_dump()
        sensitive_keys = {"SECRET_KEY", "DATABASE_URL", "SENTRY_DSN", "REDIS_URL"}
        
        for key in sensitive_keys:
            if key in settings_dict and settings_dict[key]:
                settings_dict[key] = "****"
        
        return settings_dict

    class Config:
        validate_assignment = True

@lru_cache
def get_settings() -> Settings:
    """Creates singleton instance of settings."""
    return Settings()

# Instance with environment validation
settings = get_settings()

# Validate critical settings for production
if settings.SENTRY_ENVIRONMENT == EnvironmentType.PRODUCTION:
    assert settings.SECRET_KEY != "seu_segredo_aqui", "Default secret key cannot be used in production"
    assert settings.SENTRY_DSN, "Sentry DSN must be set in production"
    assert not settings.DEBUG, "Debug mode must be disabled in production"