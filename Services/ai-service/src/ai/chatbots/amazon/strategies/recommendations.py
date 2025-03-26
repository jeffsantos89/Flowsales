from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import asyncio
import httpx
from functools import wraps

from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from utils.cache import TTLCache

@dataclass(frozen=True)
class Product:
    """Immutable data class representing a product"""
    id: str
    name: str
    category: str
    price: float
    rating: float
    reviews_count: int
    last_updated: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'last_updated': self.last_updated.isoformat()
        }

class RecommendationStrategy(ABC):
    """Abstract base class for recommendation strategies"""
    
    def __init__(self, cache: Optional[TTLCache] = None):
        self.cache = cache or TTLCache()
    
    @abstractmethod
    async def get_recommendations(self, user_id: str, context: Dict[str, Any]) -> List[Product]:
        """Get recommendations based on strategy"""
        pass

    async def _cache_wrapper(self, key: str, func, *args, **kwargs) -> Any:
        """Generic cache wrapper for strategy methods"""
        cached = self.cache.get(key)
        if cached:
            logger.info(f"Cache hit for key: {key}")
            return cached
        result = await func(*args, **kwargs)
        self.cache.set(key, result)
        return result

class PopularityBasedStrategy(RecommendationStrategy):
    """Recommends products based on popularity metrics"""
    
    @retry(max_attempts=3, backoff=2)
    async def get_recommendations(self, user_id: str, context: Dict[str, Any]) -> List[Product]:
        try:
            cache_key = f"popularity::{user_id}::{hash(frozenset(context.items()))}"
            return await self._cache_wrapper(cache_key, self._calculate_popularity_score, context)
        except Exception as e:
            logger.error(f"Error in popularity recommendations: {str(e)}")
            return []

    async def _calculate_popularity_score(self, context: Dict[str, Any]) -> List[Product]:
        # Implementation here
        return []

class CollaborativeFilteringStrategy(RecommendationStrategy):
    """Recommends products based on similar user behaviors"""
    
    @retry(max_attempts=3, backoff=2)
    async def get_recommendations(self, user_id: str, context: Dict[str, Any]) -> List[Product]:
        try:
            cache_key = f"collaborative::{user_id}::{hash(frozenset(context.items()))}"
            return await self._cache_wrapper(cache_key, self._get_collaborative_recommendations, user_id, context)
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {str(e)}")
            return []

    async def _get_collaborative_recommendations(self, user_id: str, context: Dict[str, Any]) -> List[Product]:
        similar_users = await self._find_similar_users(user_id)
        return await self._get_recommendations_from_similar_users(similar_users)

    async def _find_similar_users(self, user_id: str) -> List[str]:
        # Implementation here
        return []

    async def _get_recommendations_from_similar_users(self, similar_users: List[str]) -> List[Product]:
        # Implementation here
        return []

class RecommendationEngine:
    """Production-ready recommendation engine with advanced features"""
    
    def __init__(self, cache: Optional[TTLCache] = None):
        self.cache = cache or TTLCache()
        self.strategies = {
            'popularity': PopularityBasedStrategy(self.cache),
            'collaborative': CollaborativeFilteringStrategy(self.cache)
        }
        self.api_endpoint = "https://api.amazon.fake/v1/recommendations"
        self._client = None

    @property
    async def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15)
        return self._client

    @retry(max_attempts=3, backoff=2)
    @background_task
    async def get_recommendations(
        self,
        user_id: str,
        strategy_name: str = 'popularity',
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Enhanced recommendation fetching with monitoring and error handling
        """
        context = context or {}
        start_time = datetime.now()

        try:
            strategy = self.strategies.get(strategy_name)
            if not strategy:
                logger.warning(f"Strategy {strategy_name} not found, using popularity")
                strategy = self.strategies['popularity']

            recommendations = await strategy.get_recommendations(user_id, context)
            filtered_recommendations = await self._apply_filters(recommendations, context, limit)

            return {
                'recommendations': [r.to_dict() for r in filtered_recommendations],
                'user_id': user_id,
                'strategy': strategy_name,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

        except Exception as e:
            logger.exception(f"Error getting recommendations for user {user_id}")
            return {'error': str(e), 'user_id': user_id}

    async def _apply_filters(
        self,
        recommendations: List[Product],
        context: Dict[str, Any],
        limit: int
    ) -> List[Product]:
        """Apply business rules and filters to recommendations"""
        # Add filtering logic here
        return recommendations[:limit]

    async def close(self):
        """Cleanup resources"""
        if self._client:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# Usage example
async def main():
    async with RecommendationEngine() as engine:
        result = await engine.get_recommendations(
            user_id="user123",
            strategy_name="collaborative",
            context={"category": "electronics"},
            limit=5
        )
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
