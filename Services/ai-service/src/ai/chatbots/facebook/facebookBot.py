from typing import Dict, Optional, Any, List, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
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
from ai.metrics.prometheus import PrometheusMetrics
from config import Settings
from src.clients.facebook_client import FacebookClient
from src.clients.google_client import GoogleClient
@dataclass
class Message:
    user_id: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    intent: Optional[str] = None
    sentiment: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConversationState(Enum):
    INITIAL = "initial"
    SUPPORT = "support"
    SALES = "sales"
    HANDOVER = "handover"
    ERROR = "error"

    @classmethod
    def from_intent(cls, intent: str, confidence: float, threshold: float) -> 'ConversationState':
        if confidence < threshold:
            return cls.HANDOVER
        return {
            "purchase": cls.SALES,
            "support": cls.SUPPORT
        }.get(intent, cls.INITIAL)

class MessageHandler(ABC):
    @abstractmethod
    async def handle(self, message: Message) -> Dict[str, Any]:
        pass

class FacebookChatBot:
    def __init__(
        self,
        settings: Settings,
        dependencies: Optional[Dict[str, Any]] = None
    ):
        deps = dependencies or {}
        self.settings = settings
        self.nlp = deps.get('nlp_processor', HuggingFaceProcessor())
        self.sales_db = deps.get('sales_db', SalesDatabase())
        self.ticketing = deps.get('ticketing', TicketingSystem())
        self.queue = deps.get('queue', RedisQueue())
        self.rate_limiter = deps.get('rate_limiter', RateLimiter())
        self.cache = deps.get('cache', TTLCache())
        self.metrics = deps.get('metrics', PrometheusMetrics())
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self._setup_metrics()

    def _setup_metrics(self) -> None:
        """Initialize metrics collectors"""
        self.metrics.gauge('active_conversations', 'Number of active conversations')
        self.metrics.histogram('message_processing_time', 'Message processing duration')
        self.metrics.counter('total_messages', 'Total messages processed')

    async def _analyze_intent(self, message: Message) -> ConversationState:
        try:
            with self.metrics.timer('intent_analysis_duration'):
                intent, confidence = await self.nlp.analyze_async(message.content)
                message.sentiment = await self.nlp.analyze_sentiment(message.content)
                message.intent = intent
                
                return ConversationState.from_intent(
                    intent, 
                    confidence, 
                    self.settings.MIN_CONFIDENCE_THRESHOLD
                )
        except Exception as e:
            logger.error(f"Intent analysis failed: {str(e)}", exc_info=True)
            return ConversationState.ERROR

    async def _handle_sales(self, message: Message) -> str:
        async with self.metrics.timer('sales_handling_duration'):
            try:
                products = await self.sales_db.get_recommended_products_async(
                    user_id=message.user_id,
                    sentiment=message.sentiment
                )
                return (
                    self.settings.SALES_TEMPLATE.format(
                        products=", ".join(p["name"] for p in products[:3])
                    )
                    if products
                    else self.settings.DEFAULT_SALES_MESSAGE
                )
            except Exception as e:
                logger.error(f"Sales handling failed: {str(e)}", exc_info=True)
                raise

    async def _handle_support(self, message: Message) -> str:
        async with self.metrics.timer('support_handling_duration'):
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
                        "priority": "high" if message.sentiment < 0 else "normal",
                        "metadata": message.metadata
                    }
                )
                return self.settings.SUPPORT_HANDOVER_MESSAGE
            except Exception as e:
                logger.error(f"Support handling failed: {str(e)}", exc_info=True)
                raise

    def _validate_input(self, user_id: str, query: str) -> bool:
        """Validate input parameters"""
        return bool(
            user_id 
            and isinstance(user_id, str) 
            and query 
            and isinstance(query, str)
        )

    @retry(max_attempts=3, backoff=1)
    async def handle_customer_query(
        self, 
        user_id: str, 
        query: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        self.metrics.increment('total_messages')

        try:
            if not self._validate_input(user_id, query):
                return {"error": "Invalid input parameters"}

            if await self.rate_limiter.is_blocked_async(user_id):
                self.metrics.increment('rate_limit_blocks')
                return {"error": "Rate limit exceeded"}

            cached_response = await self.cache.get_async(f"{user_id}:{query}")
            if cached_response:
                self.metrics.increment('cache_hits')
                return cached_response

            message = Message(
                user_id=user_id,
                content=query,
                timestamp=start_time,
                metadata=metadata or {}
            )

            self.conversations.setdefault(
                user_id,
                {
                    "state": ConversationState.INITIAL,
                    "start_time": start_time,
                    "messages": []
                }
            )

            intent = await self._analyze_intent(message)
            self.conversations[user_id]["messages"].append(message)

            response = await {
                ConversationState.SALES: self._handle_sales,
                ConversationState.SUPPORT: self._handle_support,
                ConversationState.ERROR: lambda m: self.settings.ERROR_MESSAGE,
            }.get(intent, lambda m: self.settings.WELCOME_MESSAGE)(message)

            result = {
                "user_id": user_id,
                "response": response,
                "state": self.conversations[user_id]["state"].value,
                "needs_human_attention": self.conversations[user_id]["state"] == ConversationState.HANDOVER,
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "metadata": message.metadata
            }

            await asyncio.gather(
                self.cache.set_async(f"{user_id}:{query}", result),
                self.queue.enqueue_async("chat_responses", result)
            )

            self.metrics.histogram(
                'response_time',
                result["processing_time"]
            )
            self.metrics.gauge('active_conversations', len(self.conversations))

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
