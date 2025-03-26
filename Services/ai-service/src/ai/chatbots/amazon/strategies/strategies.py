from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import json
from logging.handlers import RotatingFileHandler
import asyncio
from functools import wraps
import traceback
import aiohttp
import backoff
from cachetools import TTLCache
from prometheus_client import Counter, Histogram

# Enhanced logging configuration
def setup_logging():
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler('amazon_chatbot.log', maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()

# Metrics
STRATEGY_EXECUTION_TIME = Histogram('strategy_execution_seconds', 'Time spent executing strategy')
STRATEGY_FAILURES = Counter('strategy_failures_total', 'Number of strategy execution failures')

# Enhanced Strategy Types
class StrategyType(str, Enum):
    PRODUCT_SEARCH = "product_search"
    PRICE_COMPARISON = "price_comparison"
    CUSTOMER_SERVICE = "customer_service"
    ORDER_STATUS = "order_status"
    RECOMMENDATIONS = "recommendations"

    @classmethod
    def list(cls) -> List[str]:
        return [e.value for e in cls]

# Enhanced Context with validation
@dataclass
class StrategyContext:
    user_id: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    input_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = field(default=None)
    retry_count: int = field(default=0)
    max_retries: int = field(default=3)

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if not self.user_id:
            raise ValueError("user_id is required")
        if not self.session_id:
            raise ValueError("session_id is required")
        if not isinstance(self.input_data, dict):
            raise TypeError("input_data must be a dictionary")

# Result type for strategies
T = TypeVar('T')

@dataclass
class StrategyResult(Generic[T]):
    status: str
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_success(self) -> bool:
        return self.status == "success"

# Enhanced base strategy
class AmazonChatStrategy(ABC):
    def __init__(self):
        self.cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes cache

    @abstractmethod
    async def execute(self, context: StrategyContext) -> StrategyResult:
        pass

    async def _rate_limit(self):
        await asyncio.sleep(0.1)  # Basic rate limiting

    def _validate_context(self, context: StrategyContext) -> bool:
        try:
            context.validate()
            return True
        except (ValueError, TypeError) as e:
            logger.error(f"Context validation failed: {str(e)}")
            return False

    @STRATEGY_EXECUTION_TIME.time()
    async def execute_with_metrics(self, context: StrategyContext) -> StrategyResult:
        try:
            await self._rate_limit()
            result = await self.execute(context)
            self._log_execution(context, result)
            return result
        except Exception as e:
            STRATEGY_FAILURES.inc()
            logger.error(f"Strategy execution failed: {str(e)}\n{traceback.format_exc()}")
            return StrategyResult(
                status="failed",
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )

    def _log_execution(self, context: StrategyContext, result: StrategyResult) -> None:
        logger.info(
            f"Strategy executed: {self.__class__.__name__} "
            f"User: {context.user_id} "
            f"Session: {context.session_id} "
            f"Status: {result.status}"
        )

# Enhanced Product Search Strategy
class ProductSearchStrategy(AmazonChatStrategy):
    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=3)
    async def execute(self, context: StrategyContext) -> StrategyResult:
        if not self._validate_context(context):
            return StrategyResult(status="failed", error="Invalid context")

        cache_key = f"{context.user_id}:{json.dumps(context.input_data)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Implement actual product search logic here
            async with aiohttp.ClientSession() as session:
                # Simulate API call
                await asyncio.sleep(0.1)
                
            result = StrategyResult(
                status="success",
                data={
                    "type": StrategyType.PRODUCT_SEARCH.value,
                    "results": [],  # Add actual search results here
                },
                metadata={"source": "product_api"}
            )
            
            self.cache[cache_key] = result
            return result
        except Exception as e:
            logger.exception("Product search failed")
            return StrategyResult(status="failed", error=str(e))

# Enhanced Strategy Factory with dependency injection
class StrategyFactory:
    def __init__(self):
        self._strategies: Dict[StrategyType, AmazonChatStrategy] = {}
        self._register_default_strategies()

    def _register_default_strategies(self):
        self.register_strategy(StrategyType.PRODUCT_SEARCH, ProductSearchStrategy())
        # Register other strategies...

    def register_strategy(self, strategy_type: StrategyType, strategy: AmazonChatStrategy):
        self._strategies[strategy_type] = strategy

    def get_strategy(self, strategy_type: StrategyType) -> AmazonChatStrategy:
        if strategy_type not in self._strategies:
            raise ValueError(f"Strategy not found: {strategy_type}")
        return self._strategies[strategy_type]

# Enhanced Strategy Executor with retry and circuit breaker
class StrategyExecutor:
    def __init__(self, factory: Optional[StrategyFactory] = None):
        self.factory = factory or StrategyFactory()
        self._circuit_breaker_failures = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_timeout = 60  # seconds

    async def execute_strategy(
        self,
        strategy_type: StrategyType,
        user_id: str,
        session_id: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        if self._is_circuit_open():
            return StrategyResult(status="failed", error="Circuit breaker is open")

        context = StrategyContext(
            user_id=user_id,
            session_id=session_id,
            input_data=input_data,
            metadata=metadata
        )

        try:
            strategy = self.factory.get_strategy(strategy_type)
            result = await strategy.execute_with_metrics(context)
            
            if not result.is_success:
                self._increment_failure_count()
            else:
                self._reset_failure_count()
                
            return result
        except Exception as e:
            self._increment_failure_count()
            logger.exception("Strategy execution failed")
            return StrategyResult(status="failed", error=str(e))

    def _is_circuit_open(self) -> bool:
        return self._circuit_breaker_failures >= self._circuit_breaker_threshold

    def _increment_failure_count(self):
        self._circuit_breaker_failures += 1

    def _reset_failure_count(self):
        self._circuit_breaker_failures = 0
