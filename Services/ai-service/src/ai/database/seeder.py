from typing import List, Optional, Dict, Any, TypeVar
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Base, User, Prediction

ModelType = TypeVar('ModelType', bound=Base) # type: ignore
from database.db_session import DatabaseSessionManager
from passlib.context import CryptContext
from enum import Enum
import sys
import asyncio
from typing import Type

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('seeder.log')
    ]
)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    REGRESSION = "REGRESSION"
    CLASSIFICATION = "CLASSIFICATION"

class PasswordManager:
    """Singleton for password management"""
    _instance: Optional['PasswordManager'] = None
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __new__(cls) -> 'PasswordManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls._pwd_context.hash(password)

class DatabaseSeeder:
    """Handles database seeding with enhanced error handling and batch processing"""
    def __init__(self):
        self._manager = DatabaseSessionManager()
        self._password_manager = PasswordManager()
        self._retry_attempts = 3
        self._batch_size = 100
        self._seed_data = self._get_seed_data()

    def _get_seed_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Centralized seed data configuration"""
        return {
            "users": [
                {
                    "name": "Admin",
                    "email": "admin@example.com",
                    "hashed_password": self._password_manager.hash_password("admin123"),
                    "created_at": datetime.utcnow(),
                    "is_active": True,
                    "role": "admin"
                },
                {
                    "name": "Test User",
                    "email": "test@example.com",
                    "hashed_password": self._password_manager.hash_password("test123"),
                    "created_at": datetime.utcnow(),
                    "is_active": True,
                    "role": "user"
                }
            ],
            "predictions": [
                {
                    "model_name": "GPT-4",
                    "model_type": ModelType.REGRESSION.value,
                    "prediction_value": 92.5,
                    "confidence_score": 0.95,
                    "metadata": {"framework": "transformers", "version": "4.0"}
                },
                {
                    "model_name": "BERT",
                    "model_type": ModelType.CLASSIFICATION.value,
                    "prediction_value": 88.7,
                    "confidence_score": 0.89,
                    "metadata": {"framework": "pytorch", "version": "2.0"}
                }
            ]
        }

    @asynccontextmanager
    async def _transaction_scope(self, session: AsyncSession):
        """Transaction management with retry logic"""
        attempt = 0
        while attempt < self._retry_attempts:
            try:
                yield session
                await session.commit()
                break
            except IntegrityError as e:
                await session.rollback()
                logger.warning(f"Integrity error on attempt {attempt + 1}: {e}")
                attempt += 1
                if attempt == self._retry_attempts:
                    raise
            except Exception as e:
                await session.rollback()
                logger.error(f"Transaction failed: {e}")
    async def _check_existing_data(self, session: AsyncSession, model: type[ModelType], filters: Dict[str, Any]) -> bool:

    async def _check_existing_data(self, session: AsyncSession, model: Type[Base], filters: Dict[str, Any]) -> bool: # type: ignore
        """Check for existing records"""
        query = select(model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

    async def _create_batch(self, session: AsyncSession, model: Type[Base], data_list: List[Dict[str, Any]], unique_key: str) -> List[Base]: # type: ignore
        """Generic batch creation with duplicate checking"""
        entities = []
        for data in data_list:
            if not await self._check_existing_data(session, model, {unique_key: data[unique_key]}):
                entity = model(**data)
                session.add(entity)
                entities.append(entity)
            else:
                logger.warning(f"{model.__name__} with {unique_key}={data[unique_key]} already exists")
        
        if entities:
            await session.flush()
        return entities

    async def _create_users(self, session: AsyncSession) -> List[User]:
        """Create users in batch"""
        return await self._create_batch(session, User, self._seed_data["users"], "email")

    async def _create_predictions(self, session: AsyncSession, users: List[User]) -> None:
        """Create predictions with user association"""
        if not users:
            logger.warning("No users available for creating predictions")
            return

        predictions_data = self._seed_data["predictions"]
        for i, data in enumerate(predictions_data):
            data["user_id"] = users[i % len(users)].id
            data["created_at"] = datetime.utcnow()

        await self._create_batch(session, Prediction, predictions_data, "model_name")

    async def seed(self) -> None:
        """Main seeding process with comprehensive error handling"""
        logger.info("Starting database seeding process...")
        
        async with self._manager.get_session() as session:
            try:
                async with self._transaction_scope(session) as ts:
                    users = await self._create_users(ts)
                    await self._create_predictions(ts, users)
                logger.info("Database seeding completed successfully")
            except Exception as e:
                logger.error(f"Seeding process failed: {str(e)}")
                raise

async def init_db():
    """Database initialization"""
    try:
        async with DatabaseSessionManager().engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(init_db())
        asyncio.run(DatabaseSeeder().seed())
    except KeyboardInterrupt:
        logger.info("Seeding process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error during seeding: {str(e)}")
        sys.exit(1)
