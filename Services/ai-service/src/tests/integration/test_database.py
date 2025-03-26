import pytest
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test database configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://user:password@localhost:5432/test_db")

@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    try:
        engine = create_engine(TEST_DATABASE_URL)
        yield engine
    finally:
        engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

class TestDatabaseConnection:
    """Test database connectivity and basic operations."""

    def test_database_connection(self, db_engine):
        """Test if we can connect to the database."""
        try:
            with db_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
                logger.info("Database connection test passed")
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {str(e)}")
            raise

    def test_session_management(self, db_session):
        """Test session creation and management."""
        assert db_session is not None
        assert isinstance(db_session, Session)

class TestDatabaseOperations:
    """Test various database operations."""

    def test_transaction_rollback(self, db_session):
        """Test transaction rollback functionality."""
        try:
            # Start a transaction
            db_session.begin()
            # Execute some test SQL
            db_session.execute(text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name TEXT)"))
            db_session.execute(text("INSERT INTO test_table (name) VALUES ('test')"))
            # Rollback the transaction
            db_session.rollback()
            logger.info("Transaction rollback test passed")
        except SQLAlchemyError as e:
            logger.error(f"Transaction rollback test failed: {str(e)}")
            raise

    def test_transaction_commit(self, db_session):
        """Test transaction commit functionality."""
        try:
            # Start a transaction
            db_session.begin()
            # Execute some test SQL
            db_session.execute(text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name TEXT)"))
            db_session.execute(text("INSERT INTO test_table (name) VALUES ('test')"))
            # Commit the transaction
            db_session.commit()
            # Verify the data was inserted
            result = db_session.execute(text("SELECT COUNT(*) FROM test_table")).scalar()
            assert result > 0
            logger.info("Transaction commit test passed")
        except SQLAlchemyError as e:
            logger.error(f"Transaction commit test failed: {str(e)}")
            raise
        finally:
            # Cleanup
            db_session.execute(text("DROP TABLE IF EXISTS test_table"))
            db_session.commit()

class TestDatabasePerformance:
    """Test database performance metrics."""

    def test_bulk_insert_performance(self, db_session):
        """Test bulk insert performance."""
        try:
            start_time = datetime.now()
            # Create test table
            db_session.execute(text("""
                CREATE TABLE IF NOT EXISTS performance_test (
                    id SERIAL PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Bulk insert
            for i in range(1000):
                db_session.execute(
                    text("INSERT INTO performance_test (data) VALUES (:data)"),
                    {"data": f"test_data_{i}"}
                )
            db_session.commit()
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Bulk insert performance test completed in {duration} seconds")
            assert duration < 10  # Assert that bulk insert takes less than 10 seconds
        except SQLAlchemyError as e:
            logger.error(f"Bulk insert performance test failed: {str(e)}")
            raise
        finally:
            # Cleanup
            db_session.execute(text("DROP TABLE IF EXISTS performance_test"))
            db_session.commit()

@pytest.fixture(autouse=True)
def setup_teardown(db_session):
    """Setup and teardown for each test."""
    # Setup
    yield
    # Teardown
    db_session.rollback()