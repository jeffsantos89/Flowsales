"""
order_tracking.py
Strategy for tracking order status (tracking code, status, delivery forecast).
"""

from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
import httpx
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from abc import ABC, abstractmethod

from utils.logger import logger
from utils.cache import TTLCache
from ai.decorators.background_task import background_task
from .base import BaseAmazonStrategy

class OrderStatus(BaseModel):
    """Data model for order tracking response"""
    order_id: str
    tracking_code: Optional[str]
    status: str
    estimated_delivery: Optional[datetime]
    last_update: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)

class OrderTrackingError(Exception):
    """Custom exception for order tracking errors"""
    pass

class TrackingProvider(ABC):
    """Abstract base class for tracking providers"""
    @abstractmethod
    async def track(self, order_id: str) -> OrderStatus:
        pass

class AmazonTrackingProvider(TrackingProvider):
    """Amazon-specific tracking implementation"""
    def __init__(self, api_endpoint: str, timeout: int = 15):
        self.api_endpoint = api_endpoint
        self.timeout = timeout

    async def track(self, order_id: str) -> OrderStatus:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(
                    self.api_endpoint,
                    params={"order_id": order_id},
                    headers={"User-Agent": "OrderTrackingService/1.0"}
                )
                resp.raise_for_status()
                data = resp.json()
                return OrderStatus(**data)
            except httpx.HTTPError as e:
                raise OrderTrackingError(f"HTTP error tracking order: {str(e)}")
            except Exception as e:
                raise OrderTrackingError(f"Unexpected error: {str(e)}")

class OrderTrackingStrategy(BaseAmazonStrategy):
    def __init__(
        self,
        cache: Optional[TTLCache] = None,
        tracking_provider: Optional[TrackingProvider] = None,
        cache_ttl: int = 3600  # 1 hour
    ):
        self.cache = cache or TTLCache()
        self.tracking_provider = tracking_provider or AmazonTrackingProvider(
            api_endpoint="https://api.amazon.fake/v1/orders/track"
        )
        self.cache_ttl = cache_ttl

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda retry_state: {"error": "Max retries reached"}
    )
    @background_task
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute order tracking strategy.
        
        Args:
            payload (Dict[str, Any]): Must contain {"order_id": "1234"}
        
        Returns:
            Dict[str, Any]: Order tracking information or error details
        """
        order_id = payload.get("order_id")
        if not order_id:
            logger.error("[OrderTrackingStrategy] Missing order_id in payload")
            return {"error": "order_id is required", "status_code": 400}

        try:
            return await self._get_tracking_info(order_id)
        except OrderTrackingError as e:
            logger.exception("[OrderTrackingStrategy] Error tracking order")
            return {"error": str(e), "status_code": 500}
        except Exception as e:
            logger.exception("[OrderTrackingStrategy] Unexpected error")
            return {"error": "Internal server error", "status_code": 500}

    async def _get_tracking_info(self, order_id: str) -> Dict[str, Any]:
        """Get tracking information from cache or provider"""
        cache_key = f"order_tracking::{order_id}"
        
        # Try to get from cache
        cached = self.cache.get(cache_key)
        if cached:
            logger.info("[OrderTrackingStrategy] Returning cached order status")
            return cached

        # Get fresh data
        logger.info(f"[OrderTrackingStrategy] Tracking order {order_id}")
        status = await self.tracking_provider.track(order_id)
        
        # Cache the result
        result = status.dict()
        self.cache.set(cache_key, result, ttl=self.cache_ttl)
        
        return result

    @classmethod
    async def create(
        cls,
        cache: Optional[TTLCache] = None,
        api_endpoint: Optional[str] = None,
        cache_ttl: int = 3600
    ) -> 'OrderTrackingStrategy':
        """Factory method for creating OrderTrackingStrategy instances"""
        provider = AmazonTrackingProvider(
            api_endpoint=api_endpoint or "https://api.amazon.fake/v1/orders/track"
        )
        return cls(cache=cache, tracking_provider=provider, cache_ttl=cache_ttl)
