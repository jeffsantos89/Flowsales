"""
shipping_status.py
Strategy for querying shipping estimates and delivery times for products.
"""

from typing import Dict, Any, Optional, NoReturn
from dataclasses import dataclass
from datetime import datetime
import asyncio
import httpx
from pydantic import BaseModel, Field
import backoff
from contextlib import asynccontextmanager

from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from utils.cache import TTLCache
from ai.exceptions import ShippingStrategyError, ValidationError
from .base import BaseAmazonStrategy

class ShippingRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    zipcode: str = Field(..., regex=r'^\d{5}-?\d{3}$')

class ShippingResponse(BaseModel):
    estimated_delivery_days: int
    shipping_cost: float
    carrier: str
    delivery_date: datetime
    service_level: str
    tracking_available: bool

@dataclass
class ApiConfig:
    base_url: str = "https://api.amazon.fake"
    version: str = "v1"
    timeout: int = 15
    max_retries: int = 3
    backoff_factor: int = 2

class ShippingStatusStrategy(BaseAmazonStrategy):
    def __init__(
        self, 
        cache: Optional[TTLCache] = None,
        api_config: Optional[ApiConfig] = None
    ):
        self.cache = cache or TTLCache()
        self.api_config = api_config or ApiConfig()
        self.api_endpoint = f"{self.api_config.base_url}/{self.api_config.version}/shipping"

    @asynccontextmanager
    async def _get_client(self):
        async with httpx.AsyncClient(
            timeout=self.api_config.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            yield client

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.HTTPStatusError),
        max_tries=3,
        jitter=backoff.full_jitter
    )
    async def _fetch_shipping_data(
        self, 
        product_id: str, 
        zipcode: str
    ) -> Dict[str, Any]:
        async with self._get_client() as client:
            params = {"product_id": product_id, "zip": zipcode}
            try:
                resp = await client.get(
                    self.api_endpoint,
                    params=params,
                    headers=self._get_headers()
                )
                resp.raise_for_status()
                return ShippingResponse(**resp.json()).dict()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code}")
                raise ShippingStrategyError(f"HTTP {e.response.status_code}")
            except Exception as e:
                logger.exception("Unexpected error in shipping request")
                raise ShippingStrategyError(str(e))

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "ShippingStatusStrategy/1.0",
            "Accept": "application/json",
            "X-Request-ID": self._generate_request_id()
        }

    @retry(max_attempts=3, backoff=2)
    @background_task
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute shipping status strategy with validation and error handling.
        
        Args:
            payload (Dict[str, Any]): Contains product_id and zipcode
            
        Returns:
            Dict[str, Any]: Shipping information or error details
        """
        try:
            request = ShippingRequest(**payload)
            cache_key = f"shipping_status::{request.product_id}::{request.zipcode}"

            if cached := self.cache.get(cache_key):
                logger.info("[ShippingStatusStrategy] Returning cached shipping status")
                return cached

            logger.info(
                f"[ShippingStatusStrategy] Querying delivery time for "
                f"product {request.product_id} to {request.zipcode}"
            )

            data = await self._fetch_shipping_data(
                request.product_id,
                request.zipcode
            )
            
            self.cache.set(
                cache_key, 
                data,
                ttl=3600  # 1 hour cache
            )
            
            return data

        except ValidationError as e:
            logger.error(f"[ShippingStatusStrategy] Validation error: {e}")
            return {"error": "Invalid input parameters", "details": str(e)}
        except ShippingStrategyError as e:
            logger.error(f"[ShippingStatusStrategy] Strategy error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.exception("[ShippingStatusStrategy] Unexpected error")
            return {"error": "Internal service error", "details": str(e)}

    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracking"""
        from uuid import uuid4
        return str(uuid4())
