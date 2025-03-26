from typing import Optional, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from database.models import User, Prediction, Sales
from logging import getLogger
from contextlib import contextmanager
from datetime import datetime

logger = getLogger(__name__)

class DashboardRepository:
    def __init__(self, db):
        self.db = db

    async def _execute_query(self, query) -> Optional[Any]:
        """Execute SQL query with error handling."""
        try:
            result = await self.db.execute(query)
            return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Database query failed: {str(e)}")
            raise

    @contextmanager
    async def error_handling(self):
        """Context manager for error handling."""
        try:
            yield
        except Exception as e:
            logger.error(f"Operation failed: {str(e)}")
            raise

    async def count_users(self) -> int:
        """Count total number of users in the system."""
        query = select(func.count(User.id))
        return await self._execute_query(query) or 0

    async def count_predictions(self) -> int:
        """Count total number of predictions in the system."""
        query = select(func.count(Prediction.id))
        return await self._execute_query(query) or 0

    async def calculate_sales(self) -> float:
        """Calculate total sales amount."""
        query = select(func.sum(Sales.total))
        return await self._execute_query(query) or 0.0

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get all dashboard statistics in a single method."""
        async with self.error_handling():
            return {
                "total_users": await self.count_users(),
                "total_predictions": await self.count_predictions(),
                "total_sales": await self.calculate_sales(),
                "timestamp": datetime.utcnow().isoformat(),
            }
