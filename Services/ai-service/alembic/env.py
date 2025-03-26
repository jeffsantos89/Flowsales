import sys
import os
import logging
import traceback
from typing import Any, Optional, Generator
from logging.config import fileConfig
from contextlib import contextmanager
from sqlalchemy import engine_from_config, pool, create_engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.engine import Engine
from tenacity import retry, stop_after_attempt, wait_exponential
from alembic import context

# Add root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("alembic.env")


class MigrationConfig:
    """Handles migration configuration and database connectivity."""

    def __init__(self) -> None:
        self.config = context.config
        self.setup_logging()
        self.load_base_model()

    def setup_logging(self) -> None:
        """Configure logging based on configuration file or defaults."""
        if self.config.config_file_name:
            fileConfig(self.config.config_file_name)

    def load_base_model(self) -> None:
        """Load SQLAlchemy Base model."""
        try:
            from database.base import Base  # type: ignore
            self.target_metadata = Base.metadata
        except ImportError:
            logger.critical("❌ Failed to import database Base model\n" + traceback.format_exc())
            sys.exit(1)

        if not self.target_metadata:
            logger.critical("❌ Base.metadata not properly loaded")
            sys.exit(1)

    @retry(
        stop=stop_after_attempt(5),  # Agora tenta 5 vezes
        wait=wait_exponential(multiplier=1, min=2, max=15),
        reraise=True
    )
    def get_database_url(self) -> str:
        """Retrieve database URL with fallback options and validation."""
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            logger.warning("⚠️ DATABASE_URL not found in environment, falling back to alembic.ini")
            db_url = self.config.get_main_option("sqlalchemy.url")

        if not db_url:
            raise ValueError("❌ No DATABASE_URL configuration found")

        if "postgresql://" not in db_url and "postgres://" not in db_url:
            raise ValueError("❌ Invalid DATABASE_URL format")

        return db_url

    @contextmanager
    def create_connection(self) -> Generator[Engine, None, None]:
        """Create database connection with proper configuration."""
        db_url = self.get_database_url()

        engine_config = {
            **dict(self.config.get_section(self.config.config_ini_section)),
            "sqlalchemy.url": db_url,
            "sqlalchemy.pool_size": 5,
            "sqlalchemy.max_overflow": 10,
            "sqlalchemy.pool_timeout": 30,
            "sqlalchemy.pool_recycle": 1800,
        }

        engine = engine_from_config(
            engine_config,
            prefix="sqlalchemy.",
            poolclass=pool.QueuePool,
        )

        try:
            yield engine
        finally:
            engine.dispose()

    def verify_connection(self, engine: Engine) -> None:
        """Verify database connectivity."""
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("✅ Database connection verified")
        except SQLAlchemyError as e:
            logger.error(f"❌ Database connection test failed: {e}")
            raise

    def run_migrations(self) -> None:
        """Execute database migrations with proper error handling."""
        try:
            with self.create_connection() as engine:
                self.verify_connection(engine)

                with engine.connect() as connection:
                    context.configure(
                        connection=connection,
                        target_metadata=self.target_metadata,
                        compare_type=True,
                        compare_server_default=True,
                    )

                    with context.begin_transaction():
                        context.run_migrations()

            logger.info("✅ Migrations completed successfully")

        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}", exc_info=True)
            sys.exit(1)


def run_migrations_online() -> None:
    """Entry point for online migrations."""
    migration_config = MigrationConfig()
    migration_config.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in offline mode (without DB connection)."""
    try:
        config = context.config
        url = config.get_main_option("sqlalchemy.url")
        if not url:
            raise ValueError("❌ No database URL available for offline mode")

        context.configure(url=url, literal_binds=True)

        with context.begin_transaction():
            context.run_migrations()

        logger.info("✅ Offline migrations completed")

    except Exception as e:
        logger.error(f"❌ Offline migration failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    if context.is_offline_mode():
        logger.info("⚡ Running migrations in offline mode")
        run_migrations_offline()
    else:
        run_migrations_online()
