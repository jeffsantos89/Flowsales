from typing import List, Optional, Tuple, Any, Generic, TypeVar
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_
from database.models import User, Prediction, SalesData
import logging
from datetime import datetime
from functools import wraps
from abc import ABC, abstractmethod
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class QueryResult:
    """Data class for standardizing query results"""
    data: Any
    total_count: Optional[int] = None
    page: Optional[int] = None
    total_pages: Optional[int] = None

def handle_db_error(func):
    """Decorator to handle database errors consistently."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

class BaseQueryBuilder(ABC, Generic[T]):
    """Abstract base class for query builders."""
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def execute_query(self, query: Any) -> T:
        pass

class QueryBuilder(BaseQueryBuilder[Any]):
    """Enhanced query builder with caching and validation capabilities."""
    
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100
    CACHE_TIMEOUT = 300  # 5 minutes in seconds

    def __init__(self, db: AsyncSession, cache_enabled: bool = False):
        super().__init__(db)
        self.cache_enabled = cache_enabled
        self._cache = {}
        self._cache_timestamps = {}

    @contextmanager
    async def transaction(self):
        """Context manager for transaction handling"""
        async with self.db.begin() as transaction:
            try:
                yield transaction
                await transaction.commit()
            except Exception:
                await transaction.rollback()
                raise

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        return (datetime.now().timestamp() - self._cache_timestamps[cache_key]) < self.CACHE_TIMEOUT

    @handle_db_error
    async def execute_query(self, query: Any) -> Any:
        """Execute a query with optional caching and timeout."""
        if self.cache_enabled:
            cache_key = str(query)
            if cache_key in self._cache and self._is_cache_valid(cache_key):
                return self._cache[cache_key]
            
        result = await self.db.execute(query)
        
        if self.cache_enabled:
            self._cache[cache_key] = result
            self._cache_timestamps[cache_key] = datetime.now().timestamp()
            
        return result

    def _validate_pagination(self, limit: Optional[int], offset: Optional[int]) -> Tuple[int, int]:
        """Validate and normalize pagination parameters."""
        if limit is not None and limit <= 0:
            raise ValueError("Limit must be greater than 0")
        if offset is not None and offset < 0:
            raise ValueError("Offset must be non-negative")
            
        return (
            min(limit or self.DEFAULT_LIMIT, self.MAX_LIMIT),
            offset or 0
        )

    def _build_date_filter(self, date_field: Any, start_date: Optional[datetime], end_date: Optional[datetime]):
        """Build date range filter."""
        filters = []
        if start_date:
            filters.append(date_field >= start_date)
        if end_date:
            filters.append(date_field <= end_date)
        return and_(*filters) if filters else None

    @handle_db_error
    async def get_user_predictions(
        self,
        user_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> QueryResult:
        """Fetch user predictions with pagination and total count."""
        if not await self.is_valid_user(user_id):
            raise ValueError("Invalid or inactive user")

        limit, offset = self._validate_pagination(limit, offset)
        
        # Count total records
        count_query = select(func.count()).select_from(Prediction).where(
            and_(Prediction.user_id == user_id, Prediction.is_active == True)
        )
        total_count = await self.execute_query(count_query)
        total_count = total_count.scalar()

        # Get paginated data
        query = (
            select(Prediction)
            .where(and_(
                Prediction.user_id == user_id,
                Prediction.is_active == True
            ))
            .order_by(Prediction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.execute_query(query)
        predictions = result.scalars().all()

        return QueryResult(
            data=predictions,
            total_count=total_count,
            page=(offset // limit) + 1,
            total_pages=(total_count + limit - 1) // limit
        )

    @handle_db_error
    async def get_top_selling_products(
        self,
        limit: int = DEFAULT_LIMIT,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None
    ) -> QueryResult:
        """Fetch top selling products with enhanced analytics."""
        limit = min(limit, self.MAX_LIMIT)
        
        date_filter = self._build_date_filter(SalesData.transaction_date, start_date, end_date)
        
        query = (
            select(
                SalesData.product_name,
                func.sum(SalesData.revenue).label('total_revenue'),
                func.count(SalesData.id).label('sales_count'),
                func.avg(SalesData.revenue).label('avg_revenue')
            )
            .group_by(SalesData.product_name)
        )

        if date_filter:
            query = query.where(date_filter)
        if category:
            query = query.where(SalesData.category == category)

        query = query.order_by(func.sum(SalesData.revenue).desc()).limit(limit)

        result = await self.execute_query(query)
        return QueryResult(data=result.all())

    @handle_db_error
    async def is_valid_user(self, user_id: int) -> bool:
        """Enhanced user validation with caching."""
        cache_key = f"user_valid_{user_id}"
        
        if self.cache_enabled and self._is_cache_valid(cache_key):
            return self._cache[cache_key]

        query = select(User).where(and_(
            User.id == user_id,
            User.is_active == True
        ))
        
        result = await self.execute_query(query)
        is_valid = result.scalar() is not None
        
        if self.cache_enabled:
            self._cache[cache_key] = is_valid
            self._cache_timestamps[cache_key] = datetime.now().timestamp()
            
        return is_valid

    def clear_cache(self):
        """Clear the query cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
