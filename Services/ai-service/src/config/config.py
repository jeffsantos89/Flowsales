from typing import Any, Dict
from pydantic import BaseSettings, validator
from functools import lru_cache
import os
from dotenv import load_dotenv
from enum import Enum

# Load environment variables
load_dotenv()

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class DatabaseSettings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = "user"
    PASSWORD: str
    NAME: str
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    TIMEOUT: int = 30

    @validator("PORT")
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    class Config:
        env_prefix = "DB_"

class RedisSettings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0
    PASSWORD: str | None = None
    SSL: bool = False

    class Config:
        env_prefix = "REDIS_"

class APISettings(BaseSettings):
    OPENAI_API_KEY: str
    BEDROCK_API_KEY: str
    
    @validator("OPENAI_API_KEY", "BEDROCK_API_KEY")
    def validate_api_keys(cls, v: str) -> str:
        if not v:
            raise ValueError("API key cannot be empty")
        return v

class Settings(BaseSettings):
    ENV: EnvironmentType = EnvironmentType.DEVELOPMENT
    DEBUG: bool = False
    SECRET_KEY: str
    
    # Nested configurations
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    api: APISettings = APISettings()

    # Kafka settings
    KAFKA_BROKERS: list[str] = ["localhost:9092"]
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    @validator("KAFKA_BROKERS")
    def validate_kafka_brokers(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one Kafka broker must be specified")
        return v

    def dict_config(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return {
            "env": self.ENV,
            "debug": self.DEBUG,
            "database": {
                "url": f"postgresql://{self.database.USER}:{self.database.PASSWORD}"
                      f"@{self.database.HOST}:{self.database.PORT}/{self.database.NAME}"
            },
            "redis": {
                "url": f"redis://:{self.redis.PASSWORD or ''}@{self.redis.HOST}:{self.redis.PORT}/{self.redis.DB}"
            }
        }

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Returns:
        Settings: Application settings
    """
    try:
        return Settings()
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {str(e)}")

# Create global settings instance
settings = get_settings()
