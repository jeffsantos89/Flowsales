from typing import Optional, List, TypeVar, Generic
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from database.models import User, Prediction
from logging import getLogger
from fastapi import HTTPException
from abc import ABC, abstractmethod
from contextlib import contextmanager

from repositories.base_repository import Base

logger = getLogger(__name__)
T = TypeVar('T', bound=DeclarativeBase)
T = TypeVar('T', bound=Base)

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class RepositoryInterface(Generic[T], ABC):
    """Abstract base class for repositories"""
    @abstractmethod
    async def get(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass

class BaseRepository(RepositoryInterface[T]):
    """Base repository with common database operations"""
    def __init__(self, db: AsyncSession, model: type[T]):
        self._db = db
        self._model = model

    async def _handle_db_operation(self, operation):
        """Generic database operation handler with error management"""
        try:
            result = await operation()
            return result
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"Database error in {self.__class__.__name__}: {str(e)}")
            raise DatabaseError(f"Database operation failed: {str(e)}")

    async def get(self, id: int) -> Optional[T]:
        """Generic get operation"""
        return await self._handle_db_operation(
            lambda: self._db.get(self._model, id)
        )

class UserRepository(BaseRepository[User]):
    """User-specific repository operations"""
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async def operation():
            result = await self._db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar()
        return await self._handle_db_operation(operation)

class PredictionRepository(BaseRepository[Prediction]):
    """Prediction-specific repository operations"""
    def __init__(self, db: AsyncSession):
        super().__init__(db, Prediction)

    async def create(self, prediction: Prediction) -> Prediction:
        """Create new prediction"""
        async def operation():
            self._db.add(prediction)
            await self._db.commit()
            await self._db.refresh(prediction)
            return prediction
        return await self._handle_db_operation(operation)

    async def get_by_user(self, user_id: int) -> List[Prediction]:
        """Get predictions by user ID"""
        async def operation():
            result = await self._db.execute(
                select(Prediction)
                .where(Prediction.user_id == user_id)
                .order_by(Prediction.created_at.desc())
            )
            return result.scalars().all()
        return await self._handle_db_operation(operation)

    async def delete(self, prediction_id: int) -> bool:
        """Delete prediction"""
        async def operation():
            prediction = await self.get(prediction_id)
            if not prediction:
                raise HTTPException(status_code=404, detail="Prediction not found")
            await self._db.delete(prediction)
            await self._db.commit()
            return True
        return await self._handle_db_operation(operation)

class RepositoryFactory:
    """Factory for creating repositories"""
    @staticmethod
    def create_user_repository(db: AsyncSession) -> UserRepository:
        return UserRepository(db)

    @staticmethod
    def create_prediction_repository(db: AsyncSession) -> PredictionRepository:
        return PredictionRepository(db)
