from typing import Optional, Generator, Any
from sqlalchemy.orm import declarative_base, sessionmaker, Session, scoped_session
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from functools import wraps
import logging
import time
from threading import Lock

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass

class Database:
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, db_url: str, pool_size: int = 5, max_overflow: int = 10, pool_timeout: int = 30):
        if not hasattr(self, '_initialized'):
            self._initialize(db_url, pool_size, max_overflow, pool_timeout)

    def _initialize(self, db_url: str, pool_size: int, max_overflow: int, pool_timeout: int) -> None:
        """Initialize database connection and settings"""
        try:
            self._engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=3600,  # Recycle connections after 1 hour
                echo=False
            )
            
            # Create thread-safe session factory
            self._session_factory = scoped_session(sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            ))
            
            self._initialized = True
            self._setup_engine_events()
            logger.info("Database initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")

    def _setup_engine_events(self) -> None:
        """Setup SQLAlchemy engine events"""
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop()
            if total > 0.5:  # Log slow queries (>500ms)
                logger.warning(f"Slow query detected: {total:.2f} seconds")

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations"""
        session: Optional[Session] = None
        try:
            session = self._session_factory()
            yield session
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Session error: {str(e)}")
            raise
        finally:
            if session:
                session.close()