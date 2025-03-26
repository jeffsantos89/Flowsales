"""
coupons.py
Strategy for validation and application of discount coupons.
Implements robust error handling, logging, metrics, and advanced caching.
"""

from typing import Dict, Any, Optional, Union
import asyncio
from datetime import datetime
import json
from dataclasses import dataclass
from decimal import Decimal

import httpx
from pydantic import BaseModel, Field
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from utils.logger import logger
from utils.metrics import metrics
from utils.cache import TTLCache
from .base import BaseAmazonStrategy
from ai.exceptions import CouponValidationError, RateLimitError

class CouponRequest(BaseModel):
    coupon_code: str = Field(..., min_length=3, max_length=50)
    cart_total: Decimal = Field(..., ge=0)

class CouponResponse(BaseModel):
    valid: bool
    discount_value: Decimal
    coupon_code: str
    expires_at: Optional[datetime]
    restrictions: Optional[Dict[str, Any]]

@dataclass
class CouponConfig:
    api_endpoint: str
    cache_ttl: int = 3600  # 1 hour
    timeout: int = 15
    max_retries: int = 3
    rate_limit: int = 100  # requests per minute

class CouponsStrategy(BaseAmazonStrategy):
    def __init__(
        self, 
        cache: Optional[TTLCache] = None,
        config: Optional[CouponConfig] = None
    ):
        self.cache = cache or TTLCache()
        self.config = config or CouponConfig(
            api_endpoint="https://api.amazon.fake/v1/coupons"
        )
        self._rate_limiter = asyncio.Semaphore(self.config.rate_limit)

    @metrics.time('coupon_validation_time')
    async def execute(
        self, 
        payload: Dict[str, Any]
    ) -> Union[CouponResponse, Dict[str, str]]:
        """
        Validates and processes coupon codes with advanced error handling and metrics.
        """
        try:
            request = CouponRequest(**payload)
            cache_key = self._generate_cache_key(request)
            
            if cached := await self._get_from_cache(cache_key):
                metrics.increment('coupon_cache_hit')
                return cached

            metrics.increment('coupon_cache_miss')
            async with self._rate_limiter:
                result = await self._process_coupon(request)
                await self._save_to_cache(cache_key, result)
                return result

        except ValueError as e:
            logger.warning(f"[CouponsStrategy] Invalid payload: {str(e)}")
            return {"error": "Invalid request parameters"}
        except CouponValidationError as e:
            logger.error(f"[CouponsStrategy] Validation error: {str(e)}")
            metrics.increment('coupon_validation_error')
            return {"error": str(e)}
        except Exception as e:
            logger.exception("[CouponsStrategy] Unexpected error")
            metrics.increment('coupon_unexpected_error')
            return {"error": "Internal service error"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.TimeoutException)
    )
    async def _process_coupon(self, request: CouponRequest) -> CouponResponse:
        """
        Process coupon validation with automatic retries and error handling.
        """
        async with httpx.AsyncClient(
            timeout=self.config.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            try:
                response = await client.get(
                    self.config.api_endpoint,
                    params={
                        "code": request.coupon_code,
                        "cart_total": str(request.cart_total)
                    }
                )
                response.raise_for_status()
                return CouponResponse(**response.json())
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise RateLimitError("API rate limit exceeded")
                raise CouponValidationError(f"API error: {e.response.status_code}")

    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Asynchronously retrieve cached coupon data."""
        if cached := self.cache.get(key):
            return json.loads(cached)
        return None

    async def _save_to_cache(self, key: str, data: Dict) -> None:
        """Asynchronously cache coupon data."""
        self.cache.set(key, json.dumps(data), ttl=self.config.cache_ttl)

    def _generate_cache_key(self, request: CouponRequest) -> str:
        """Generate a unique cache key for the coupon request."""
        return f"coupon::{request.coupon_code}::{request.cart_total}"
