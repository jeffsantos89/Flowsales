"""
review_analysis.py
Strategy for analyzing product reviews, extracting sentiment,
rating statistics, keywords, and other insights.
"""

from typing import Dict, Any, Optional, List, Union
import asyncio
from dataclasses import dataclass
from enum import Enum
import httpx
from pydantic import BaseModel, Field
import backoff
from prometheus_client import Counter, Histogram

from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from utils.cache import TTLCache
from config import settings
from .base import BaseAmazonStrategy

# Metrics
REVIEW_REQUESTS = Counter('review_analysis_requests_total', 'Total review analysis requests')
REVIEW_ERRORS = Counter('review_analysis_errors_total', 'Total review analysis errors')
REVIEW_LATENCY = Histogram('review_analysis_latency_seconds', 'Review analysis latency')

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"

class ReviewAPIError(Exception):
    """Custom exception for review API errors"""
    pass

class SentimentAPIError(Exception):
    """Custom exception for sentiment API errors"""
    pass

class Review(BaseModel):
    """Review data model"""
    id: str
    content: str
    rating: int = Field(ge=1, le=5)
    date: str
    verified_purchase: bool = False

class ReviewAnalysisResult(BaseModel):
    """Analysis result data model"""
    product_id: str
    reviews: List[Review]
    sentiment_overall: Optional[SentimentType]
    review_count: int
    average_rating: float
    sentiment_distribution: Dict[str, float]
    error: Optional[str] = None

@dataclass
class APIConfig:
    """API configuration"""
    base_url: str
    timeout: int
    max_retries: int
    backoff_factor: float

class ReviewAnalysisStrategy(BaseAmazonStrategy):
    def __init__(
        self,
        cache: Optional[TTLCache] = None,
        review_api_config: Optional[APIConfig] = None,
        sentiment_api_config: Optional[APIConfig] = None
    ):
        self.cache = cache or TTLCache()
        self.review_api_config = review_api_config or APIConfig(
            base_url=settings.REVIEW_API_URL,
            timeout=15,
            max_retries=3,
            backoff_factor=2
        )
        self.sentiment_api_config = sentiment_api_config or APIConfig(
            base_url=settings.SENTIMENT_API_URL,
            timeout=15,
            max_retries=3,
            backoff_factor=2
        )

    @retry(max_attempts=3, backoff=2)
    @background_task
    @REVIEW_LATENCY.time()
    async def execute(self, payload: Dict[str, Any]) -> ReviewAnalysisResult:
        """
        Execute review analysis with enhanced error handling and metrics
        """
        REVIEW_REQUESTS.inc()
        product_id = payload.get("product_id")
        analyze_sentiment = payload.get("analyze_sentiment", False)

        if not product_id:
            REVIEW_ERRORS.inc()
            return ReviewAnalysisResult(
                product_id="",
                reviews=[],
                sentiment_overall=None,
                review_count=0,
                average_rating=0.0,
                sentiment_distribution={},
                error="product_id not provided"
            )

        try:
            cache_key = f"review_analysis::{product_id}::{analyze_sentiment}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("[ReviewAnalysisStrategy] Returning cached review analysis")
                return ReviewAnalysisResult(**cached)

            reviews = await self._fetch_reviews(product_id)
            sentiment_data = None
            if analyze_sentiment and reviews:
                sentiment_data = await self._analyze_reviews_sentiment(reviews)

            result = self._prepare_analysis_result(product_id, reviews, sentiment_data)
            self.cache.set(cache_key, result.dict())
            return result

        except Exception as e:
            REVIEW_ERRORS.inc()
            logger.exception("[ReviewAnalysisStrategy] Error analyzing reviews")
            return ReviewAnalysisResult(
                product_id=product_id,
                reviews=[],
                sentiment_overall=None,
                review_count=0,
                average_rating=0.0,
                sentiment_distribution={},
                error=str(e)
            )

    @backoff.on_exception(
        backoff.expo,
        (httpx.HTTPError, asyncio.TimeoutError),
        max_tries=3
    )
    async def _fetch_reviews(self, product_id: str) -> List[Review]:
        async with httpx.AsyncClient(
            timeout=self.review_api_config.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            resp = await client.get(
                f"{self.review_api_config.base_url}/reviews",
                params={"product_id": product_id}
            )
            resp.raise_for_status()
            data = resp.json()
            return [Review(**review) for review in data.get("reviews", [])]

    async def _analyze_reviews_sentiment(
        self,
        reviews: List[Review]
    ) -> Dict[str, Union[str, Dict[str, float]]]:
        async with httpx.AsyncClient(
            timeout=self.sentiment_api_config.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            review_texts = [r.content for r in reviews]
            resp = await client.post(
                f"{self.sentiment_api_config.base_url}/analyze",
                json={"reviews": review_texts}
            )
            resp.raise_for_status()
            return resp.json()

    def _prepare_analysis_result(
        self,
        product_id: str,
        reviews: List[Review],
        sentiment_data: Optional[Dict[str, Any]]
    ) -> ReviewAnalysisResult:
        review_count = len(reviews)
        average_rating = sum(r.rating for r in reviews) / review_count if review_count > 0 else 0.0
        
        return ReviewAnalysisResult(
            product_id=product_id,
            reviews=reviews,
            sentiment_overall=sentiment_data.get("overall_sentiment", SentimentType.UNKNOWN) if sentiment_data else None,
            review_count=review_count,
            average_rating=round(average_rating, 2),
            sentiment_distribution=sentiment_data.get("sentiment_distribution", {}) if sentiment_data else {}
        )
