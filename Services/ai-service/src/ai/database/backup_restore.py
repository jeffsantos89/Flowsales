import os
from datetime import datetime
import subprocess
import logging
from pathlib import Path
from typing import Optional
import sys

class DatabaseConfig:
    def __init__(self):
        self.name = os.getenv("DATABASE_NAME", "ai_service")
        self.user = os.getenv("DATABASE_USER", "postgres")
        self.password = os.getenv("DATABASE_PASSWORD", "password")
        self.host = os.getenv("DATABASE_HOST", "localhost")
        self.port = os.getenv("DATABASE_PORT", "5432")

class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.backup_dir = Path(os.getcwd()) / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging with both file and console handlers."""
        self.logger = logging.getLogger('DatabaseManager')
        self.logger.setLevel(logging.INFO)

        # File handler
        log_file = self.backup_dir / f'db_operations_{datetime.now():%Y%m%d}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(console_handler)

    def _get_env(self) -> dict:
        """Return environment variables for database operations."""
        env = os.environ.copy()
        env['PGPASSWORD'] = self.config.password
        return env

    def backup_database(self) -> Optional[Path]:
        """
        Execute database backup with logging and error handling.
        Returns the backup file path if successful, None otherwise.
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"backup_{self.config.name}_{timestamp}.sql"

            self.logger.info(f"Starting backup to {backup_file}")

            result = subprocess.run(
                [
                    'pg_dump',
                    '-U', self.config.user,
                    '-h', self.config.host,
                    '-p', self.config.port,
                    '--format=p',  # plain text format
                    '--no-owner',  # skip ownership commands
                    '--no-privileges',  # skip privilege commands
                    self.config.name
                ],
                env=self._get_env(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            with open(backup_file, 'w') as f:
                f.write(result.stdout)

            self.logger.info(f"Backup created successfully: {backup_file}")
            return backup_file

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Backup failed: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during backup: {str(e)}")
            raise

    def restore_database(self, backup_file: Path) -> bool:
        """
        Restore database from backup file.
        Returns True if successful, False otherwise.
        """
        try:
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")

            self.logger.info(f"Starting restore from {backup_file}")

            result = subprocess.run(
                [
                    'psql',
                    '-U', self.config.user,
                    '-h', self.config.host,
                    '-p', self.config.port,
                    '-d', self.config.name,
                    '-f', str(backup_file)
                ],
                env=self._get_env(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            self.logger.info("Database restored successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Restore failed: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during restore: {str(e)}")
            raise

def main():
    try:
        config = DatabaseConfig()
        db_manager = DatabaseManager(config)
        backup_file = db_manager.backup_database()
        
        # Uncomment the following line to test restore
        # if backup_file:
        #     db_manager.restore_database(backup_file)

    except Exception as e:
        logging.error(f"Operation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()