from typing import Optional
from functools import lru_cache
from datetime import datetime, timedelta
from repositories.dashboard_repository import DashboardRepository
from schemas.dashboard_schema import DashboardResponse, User
from core.metrics import MetricsCollector
from core.cache import Cache
from core.exceptions import DashboardServiceException
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(
        self,
        db,
        repository: Optional[DashboardRepository] = None,
        cache: Optional[Cache] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        cache_ttl: int = 300  # 5 minutes cache
    ):
        self.db = db
        self.repository = repository or DashboardRepository(db)
        self.cache = cache
        self.metrics_collector = metrics_collector
        self.cache_ttl = cache_ttl

    @lru_cache(maxsize=128)
    async def get_dashboard_metrics(self, user: User) -> DashboardResponse:
        """
        Retrieve dashboard metrics for a user with caching, metrics collection and error handling.
        
        Args:
            user (User): The user requesting dashboard data
            
        Returns:
            DashboardResponse: Dashboard metrics data
            
        Raises:
            DashboardServiceException: If there's an error fetching the metrics
        """
        start_time = datetime.now()
        cache_key = f"dashboard_metrics:{user.email}"

        try:
            # Try to get from cache first
            if self.cache:
                cached_data = await self.cache.get(cache_key)
                if cached_data:
                    logger.debug(f"Cache hit for dashboard metrics - user: {user.email}")
                    return cached_data

            logger.info(f"Fetching dashboard metrics for user: {user.email}")
            
            # Fetch all metrics concurrently
            total_users, total_predictions, total_sales = await asyncio.gather(
                self.repository.count_users(),
                self.repository.count_predictions(),
                self.repository.calculate_sales()
            )

            response = DashboardResponse(
                total_users=total_users,
                total_predictions=total_predictions,
                total_sales=total_sales,
                last_updated=datetime.utcnow()
            )

            # Store in cache
            if self.cache:
                await self.cache.set(cache_key, response, ttl=self.cache_ttl)

            # Record metrics
            if self.metrics_collector:
                elapsed_time = (datetime.now() - start_time).total_seconds()
                self.metrics_collector.record_latency("dashboard_metrics", elapsed_time)
                self.metrics_collector.increment_counter("dashboard_requests")

            return response

        except Exception as e:
            logger.error(f"Error fetching dashboard metrics for {user.email}: {str(e)}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("dashboard_errors")
            raise DashboardServiceException(f"Failed to fetch dashboard metrics: {str(e)}")

    async def refresh_cache(self, user: User) -> None:
        """Force refresh of cached dashboard metrics"""
        self.get_dashboard_metrics.cache_clear()
        await self.get_dashboard_metrics(user)
