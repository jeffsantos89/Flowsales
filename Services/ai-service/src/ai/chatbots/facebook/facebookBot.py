from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
import asyncio
from abc import ABC, abstractmethod

from ai.nlp.huggingface_processor import HuggingFaceProcessor
from ai.queue.redis_backend import RedisQueue
from ai.database.sales import SalesDatabase
from ai.ticketing import TicketingSystem
from security.ratelimiter import RateLimiter
from utils.cache import TTLCache
from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from ai.metrics.prometheus import PrometheusMetrics
from input_validator import InputValidator # type: ignore
from config import Settings

@dataclass
class Message:
    user_id: str
    content: str
    timestamp: datetime
    intent: Optional[str] = None
    sentiment: Optional[float] = None

class ConversationState(Enum):
    INITIAL = "initial"
    SUPPORT = "support"
    SALES = "sales"
    HANDOVER = "handover"
    ERROR = "error"

class MessageHandler(ABC):
    @abstractmethod
    async def handle(self, message: Message) -> Dict[str, Any]:
        pass

class FacebookChatBot:
    def __init__(
        self,
        settings: Settings,
        nlp_processor: Optional[HuggingFaceProcessor] = None,
        sales_db: Optional[SalesDatabase] = None,
        ticketing: Optional[TicketingSystem] = None,
        queue: Optional[RedisQueue] = None,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[TTLCache] = None,
        metrics: Optional[PrometheusMetrics] = None
    ):
        self.settings = settings
        self.nlp = nlp_processor or HuggingFaceProcessor()
        self.sales_db = sales_db or SalesDatabase()
        self.ticketing = ticketing or TicketingSystem()
        self.queue = queue or RedisQueue()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.cache = cache or TTLCache()
        self.metrics = metrics or PrometheusMetrics()
        self.validator = InputValidator()
        self.conversations: Dict[str, Dict[str, Any]] = {}

    async def _analyze_intent(self, message: Message) -> ConversationState:
        try:
            with self.metrics.timer('intent_analysis_duration'):
                intent, confidence = await self.nlp.analyze_async(message.content)
                sentiment = await self.nlp.analyze_sentiment(message.content)
                
                message.intent = intent
                message.sentiment = sentiment

                if confidence < self.settings.MIN_CONFIDENCE_THRESHOLD:
                    return ConversationState.HANDOVER

                return {
                    "purchase": ConversationState.SALES,
                    "support": ConversationState.SUPPORT
                }.get(intent, ConversationState.INITIAL)
        except Exception as e:
            logger.error(f"Intent analysis failed: {str(e)}")
            return ConversationState.ERROR

    async def _handle_sales(self, message: Message) -> str:
        try:
            products = await self.sales_db.get_recommended_products_async(
                user_id=message.user_id,
                sentiment=message.sentiment
            )
            if not products:
                return self.settings.DEFAULT_SALES_MESSAGE
            
            return self.settings.SALES_TEMPLATE.format(
                products=", ".join(p["name"] for p in products[:3])
            )
        except Exception as e:
            logger.error(f"Sales handling failed: {str(e)}")
            raise

    async def _handle_support(self, message: Message) -> str:
        try:
            self.conversations[message.user_id]["state"] = ConversationState.HANDOVER
            ticket = await self.ticketing.create_ticket_async(
                user_id=message.user_id,
                query=message.content,
                sentiment=message.sentiment
            )
            await self.queue.enqueue_async(
                "support_tickets",
                {
                    "ticket_id": ticket,
                    "priority": "high" if message.sentiment < 0 else "normal"
                }
            )
            return self.settings.SUPPORT_HANDOVER_MESSAGE
        except Exception as e:
            logger.error(f"Support handling failed: {str(e)}")
            raise

    @retry(max_attempts=3, backoff=1)
    async def handle_customer_query(self, user_id: str, query: str) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        
        try:
            # Input validation
            if not self.validator.is_valid_input(user_id, query):
                return {"error": "Invalid input parameters"}

            # Rate limiting
            if await self.rate_limiter.is_blocked_async(user_id):
                self.metrics.increment('rate_limit_blocks')
                return {"error": "Rate limit exceeded"}

            # Cache check
            cached_response = await self.cache.get_async(user_id, query)
            if cached_response:
                self.metrics.increment('cache_hits')
                return cached_response

            # Create message object
            message = Message(
                user_id=user_id,
                content=query,
                timestamp=start_time
            )

            # Initialize or get conversation state
            if user_id not in self.conversations:
                self.conversations[user_id] = {
                    "state": ConversationState.INITIAL,
                    "start_time": start_time,
                    "messages": []
                }

            # Analyze intent and handle accordingly
            intent = await self._analyze_intent(message)
            self.conversations[user_id]["messages"].append(message)

            response = None
            if intent == ConversationState.SALES:
                response = await self._handle_sales(message)
            elif intent == ConversationState.SUPPORT:
                response = await self._handle_support(message)
            elif intent == ConversationState.ERROR:
                response = self.settings.ERROR_MESSAGE
            else:
                response = self.settings.WELCOME_MESSAGE

            result = {
                "user_id": user_id,
                "response": response,
                "state": self.conversations[user_id]["state"].value,
                "needs_human_attention": self.conversations[user_id]["state"] == ConversationState.HANDOVER,
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
            }

            # Cache and queue the result
            await asyncio.gather(
                self.cache.set_async(user_id, query, result),
                self.queue.enqueue_async("chat_responses", result)
            )

            self.metrics.histogram(
                'response_time',
                result["processing_time"]
            )

            return result

        except Exception as e:
            logger.exception("Critical error in FacebookBot")
            self.metrics.increment('errors')
            
            return {
                "user_id": user_id,
                "response": self.settings.ERROR_MESSAGE,
                "state": ConversationState.ERROR.value,
                "needs_human_attention": True,
                "error": str(e)
            }

class InputValidator:
    def is_valid_input(self, user_id: str, query: str) -> bool:
        if not user_id or not isinstance(user_id, str):
            return False
        if not query or not isinstance(query, str):
            return False
        return True
