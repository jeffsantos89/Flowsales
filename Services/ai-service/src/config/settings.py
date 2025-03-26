# src/config/settings.py
import os
from typing import Dict, Any
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import validator, PostgresDsn, RedisDsn, Field
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class DatabaseSettings(BaseSettings):
    HOST: str = Field(..., env="DB_HOST")
    PORT: int = Field(5432, env="DB_PORT")
    USER: str = Field(..., env="DB_USER")
    PASSWORD: str = Field(..., env="DB_PASSWORD")
    NAME: str = Field(..., env="DB_NAME")
    POOL_SIZE: int = Field(20, env="DB_POOL_SIZE")
    MAX_OVERFLOW: int = Field(10, env="DB_MAX_OVERFLOW")

    @property
    def URL(self) -> PostgresDsn:
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

class RedisSettings(BaseSettings):
    HOST: str = Field("localhost", env="REDIS_HOST")
    PORT: int = Field(6379, env="REDIS_PORT")
    DB: int = Field(0, env="REDIS_DB")
    SSL: bool = Field(False, env="REDIS_SSL")

    @property
    def URL(self) -> RedisDsn:
        protocol = "rediss" if self.SSL else "redis"
        return f"{protocol}://{self.HOST}:{self.PORT}/{self.DB}"

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "AI-Service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, env="ENV")
    DEBUG: bool = Field(False, env="DEBUG")
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    # Service configurations
    DATABASE: DatabaseSettings = DatabaseSettings()
    REDIS: RedisSettings = RedisSettings()
    KAFKA_BROKER: str = Field("localhost:9092", env="KAFKA_BROKER")
    QUANTUM_PROVIDER: str = Field("AzureQuantum", env="QUANTUM_PROVIDER")

    # Security settings
    CORS_ORIGINS: list[str] = Field(default=["*"])
    API_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    def get_environment_settings(self) -> Dict[str, Any]:
        return {
            Environment.DEVELOPMENT: {
                "DEBUG": True,
                "LOG_LEVEL": LogLevel.DEBUG,
            },
            Environment.STAGING: {
                "DEBUG": False,
                "LOG_LEVEL": LogLevel.INFO,
            },
            Environment.PRODUCTION: {
                "DEBUG": False,
                "LOG_LEVEL": LogLevel.WARNING,
            }
        }.get(self.ENVIRONMENT, {})

@lru_cache()
def get_settings() -> Settings:
    """
    Create and return a cached instance of the Settings class.
    Uses LRU cache to avoid reading the environment multiple times.
    """
    return Settings()

settings = get_settings()
