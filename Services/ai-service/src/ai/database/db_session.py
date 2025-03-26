from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import os
from functools import lru_cache
import logging
from typing import Any
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database.log')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configuration class for database settings with validation."""
    def __init__(self):
        self.DATABASE_URL = self._get_required_env("DATABASE_URL", 
            "postgresql+asyncpg://user:password@localhost/ai_service")
        self.POOL_SIZE = self._validate_int_env("DB_POOL_SIZE", 5, 1, 100)
        self.MAX_OVERFLOW = self._validate_int_env("DB_MAX_OVERFLOW", 10, 0, 100)
        self.POOL_TIMEOUT = self._validate_int_env("DB_POOL_TIMEOUT", 30, 1, 300)
        self.ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
        self.POOL_RECYCLE = self._validate_int_env("DB_POOL_RECYCLE", 3600, 1, 86400)
        self.CONNECT_RETRIES = self._validate_int_env("DB_CONNECT_RETRIES", 3, 1, 10)

    @staticmethod
    def _get_required_env(key: str, default: str) -> str:
        value = os.getenv(key, default)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    @staticmethod
    def _validate_int_env(key: str, default: int, min_val: int, max_val: int) -> int:
        try:
            value = int(os.getenv(key, str(default)))
            if not min_val <= value <= max_val:
                raise ValueError
            return value
        except ValueError:
            raise ValueError(
                f"Invalid value for {key}. Must be between {min_val} and {max_val}"
            )

class DatabaseSessionManager:
    """Manages database sessions and connection lifecycle."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._engine = None
            self._sessionmaker = None
            self._initialized = True
            self._last_connection_check = None
            self._config = None

    async def init(self, config: Optional[DatabaseConfig] = None) -> None:
        """Initialize the database connection."""
        if self._engine is not None:
            return

        self._config = config or get_db_config()
        retries = self._config.CONNECT_RETRIES

        while retries > 0:
            try:
                self._engine = create_engine(self._config)
                self._sessionmaker = sessionmaker(
                    self._engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=False
                )
                # Test the connection
                async with self.get_session() as session:
                    await session.execute("SELECT 1")
                logger.info("Database connection established successfully")
                self._last_connection_check = datetime.now()
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    logger.critical(f"Failed to connect to database after all retries: {e}")
                    raise
                logger.warning(f"Database connection attempt failed. Retrying... ({retries} attempts left)")

    async def close(self) -> None:
        """Close the database connection."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info("Database connection closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with automatic cleanup."""
        if self._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            await session.close()

    @property
    def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        return bool(self._engine and self._last_connection_check)

@lru_cache()
def get_db_config() -> DatabaseConfig:
    """Get database configuration with caching."""
    return DatabaseConfig()

def create_engine(config: DatabaseConfig) -> Any:
    """Create SQLAlchemy engine with configured parameters."""
    return create_async_engine(
        config.DATABASE_URL,
        echo=config.ECHO,
        future=True,
        pool_size=config.POOL_SIZE,
        max_overflow=config.MAX_OVERFLOW,
        pool_timeout=config.POOL_TIMEOUT,
        pool_pre_ping=True,
        pool_recycle=config.POOL_RECYCLE,
    )
