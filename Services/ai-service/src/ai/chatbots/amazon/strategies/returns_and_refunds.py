"""
returns_and_refunds.py
Strategy for handling return and refund requests with enhanced error handling,
validation, and monitoring capabilities.
"""

from typing import Dict, Any, Optional, Union
import asyncio
import httpx
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
from enum import Enum

from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from utils.cache import TTLCache
from utils.metrics import metrics
from .base import BaseAmazonStrategy

class ReturnReason(Enum):
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    NOT_AS_DESCRIBED = "not_as_described"
    NO_LONGER_NEEDED = "no_longer_needed"
    OTHER = "other"

class ReturnRequest(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=50)
    reason: ReturnReason
    refund_requested: bool = Field(default=False)
    customer_notes: Optional[str] = Field(default=None, max_length=500)

class ReturnResponse(BaseModel):
    return_id: str
    status: str
    created_at: datetime
    estimated_completion: Optional[datetime]
    tracking_number: Optional[str]

class ReturnsAndRefundsStrategy(BaseAmazonStrategy):
    def __init__(
        self, 
        cache: Optional[TTLCache] = None,
        api_endpoint: Optional[str] = None,
        timeout: int = 15
    ):
        self.cache = cache or TTLCache()
        self.api_endpoint = api_endpoint or "https://api.amazon.fake/v1/returns"
        self.timeout = timeout
        self.logger = structlog.get_logger(__name__)

    @retry(max_attempts=3, backoff=2, exceptions=(httpx.HTTPError, asyncio.TimeoutError))
    @background_task
    @metrics.track_execution_time("returns_processing")
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process return/refund requests with validation and error handling.
        
        Args:
            payload: Dictionary containing return request details
            
        Returns:
            Dictionary containing return response or error details
        """
        try:
            # Validate input
            return_request = ReturnRequest(**payload)
            
            # Check cache for existing return
            cache_key = f"return_{return_request.order_id}"
            if cached_response := self.cache.get(cache_key):
                self.logger.info("return_request_cached", order_id=return_request.order_id)
                return cached_response

            # Process return
            self.logger.info(
                "processing_return_request",
                order_id=return_request.order_id,
                reason=return_request.reason.value
            )

            result = await self._initiate_return(return_request)
            
            # Cache successful response
            self.cache.set(cache_key, result, ttl=3600)  # Cache for 1 hour
            
            return result

        except ValueError as e:
            self.logger.error("validation_error", error=str(e))
            return {"error": "Invalid input data", "details": str(e)}
        except Exception as e:
            self.logger.exception(
                "return_processing_error",
                error=str(e),
                order_id=payload.get("order_id")
            )
            metrics.increment("returns_processing_errors")
            return {"error": "Internal processing error", "reference": str(datetime.utcnow())}

    async def _initiate_return(self, return_request: ReturnRequest) -> Dict[str, Any]:
        """Initiate the return request with the Amazon API."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    self.api_endpoint,
                    json=return_request.dict(),
                    headers=self._get_request_headers()
                )
                resp.raise_for_status()
                
                return_response = ReturnResponse(**resp.json())
                return return_response.dict()

            except httpx.HTTPStatusError as e:
                self.logger.error(
                    "api_error",
                    status_code=e.response.status_code,
                    response=e.response.text
                )
                raise

    def _get_request_headers(self) -> Dict[str, str]:
        """Get headers for API request."""
        return {
            "Content-Type": "application/json",
            "X-Request-ID": metrics.generate_request_id(),
            "User-Agent": "ReturnsService/1.0"
        }
