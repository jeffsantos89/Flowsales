# amazon_bot.py
from typing import Optional, Dict, Any, Protocol, Type
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from functools import wraps
import asyncio
from datetime import datetime

from ai.chatbots.product_database import ProductDatabase
from ai.nlp.huggingface_processor import HuggingFaceProcessor
from ai.queue.redis_backend import RedisQueue
from ai.database.sales import SalesDatabase
from ai.ticketing import TicketingSystem
from security.ratelimiter import RateLimiter
from utils.cache import TTLCache
from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from .strategies.handler import AmazonStrategyHandler, StrategyNotFoundError

# Domain Models
@dataclass
class Message:
    user_id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class ProcessingResult:
    status: str
    data: Dict[str, Any]
    errors: Optional[list] = None
    processing_time: float = 0.0

class IntentType(Enum):
    PRODUCT_INFO = "product_info"
    PRICE_COMPARISON = "price_comparison"
    RECOMMENDATIONS = "recommendations"
    SUPPORT = "support"
    UNKNOWN = "unknown"

# Handler Protocol
class MessageHandler(Protocol):
    async def handle(self, message: Message) -> ProcessingResult:
        ...

# Abstract Handler
class BaseHandler(ABC):
    @abstractmethod
    async def handle(self, message: Message) -> ProcessingResult:
        pass

    def next_handler(self, handler: 'BaseHandler') -> 'BaseHandler':
        self._next_handler = handler
        return handler

# Concrete Handlers
class ValidationHandler(BaseHandler):
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self._next_handler = None

    async def handle(self, message: Message) -> ProcessingResult:
        if self.rate_limiter.is_blocked(message.user_id):
            return ProcessingResult(
                status="error",
                data={"message": "Rate limit exceeded"},
                errors=["RATE_LIMIT_EXCEEDED"]
            )
        return await self._next_handler.handle(message)

class IntentClassificationHandler(BaseHandler):
    def __init__(self, nlp_processor: HuggingFaceProcessor):
        self.nlp = nlp_processor
        self._next_handler = None

    async def handle(self, message: Message) -> ProcessingResult:
        intent = self.nlp.analyze(message.content)
        message.metadata['intent'] = intent
        return await self._next_handler.handle(message)

class StrategyExecutionHandler(BaseHandler):
    def __init__(self, strategy_handler: AmazonStrategyHandler):
        self.strategy_handler = strategy_handler
        self._next_handler = None

    async def handle(self, message: Message) -> ProcessingResult:
        intent = message.metadata.get('intent')
        try:
            payload = {"query": message.content, "user_id": message.user_id}
            result = self.strategy_handler.handle(intent, payload)
            return ProcessingResult(status="success", data=result)
        except StrategyNotFoundError as e:
            return ProcessingResult(
                status="error",
                data={"message": str(e)},
                errors=["STRATEGY_NOT_FOUND"]
            )

class AmazonChatBot:
    def __init__(
        self,
        product_db: Optional[ProductDatabase] = None,
        nlp_processor: Optional[HuggingFaceProcessor] = None,
        queue: Optional[RedisQueue] = None,
        sales_db: Optional[SalesDatabase] = None,
        ticketing: Optional[TicketingSystem] = None,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[TTLCache] = None,
    ):
        # Initialize dependencies
        self.product_db = product_db or ProductDatabase()
        self.nlp = nlp_processor or HuggingFaceProcessor()
        self.queue = queue or RedisQueue()
        self.sales_db = sales_db or SalesDatabase()
        self.ticketing = ticketing or TicketingSystem()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.cache = cache or TTLCache()

        # Initialize strategy handler
        self.strategy_handler = AmazonStrategyHandler(
            product_db=self.product_db,
            sales_db=self.sales_db,
            cache=self.cache
        )

        # Setup handler chain
        self.handler_chain = self._setup_handler_chain()

    def _setup_handler_chain(self) -> BaseHandler:
        validation_handler = ValidationHandler(self.rate_limiter)
        intent_handler = IntentClassificationHandler(self.nlp)
        strategy_handler = StrategyExecutionHandler(self.strategy_handler)

        validation_handler.next_handler(intent_handler)
        intent_handler.next_handler(strategy_handler)

        return validation_handler

    @retry(max_attempts=3, backoff=2)
    @background_task
    async def process_message(self, user_id: str, query: str) -> Dict[str, Any]:
        """Process incoming message through the handler chain."""
        # Check cache first
        cached = self.cache.get(user_id, query)
        if cached:
            return cached

        start_time = datetime.now()

        # Create message object
        message = Message(
            user_id=user_id,
            content=query,
            timestamp=start_time,
            metadata={}
        )

        try:
            # Process through handler chain
            result = await self.handler_chain.handle(message)
            
            # Update processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()

            # Cache successful results
            if result.status == "success":
                self.cache.set(user_id, query, result.data)
                # Async queue processing
                await self.queue.enqueue("amazon_responses", result.data)

            return result.data

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "status": "error",
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR"
            }
