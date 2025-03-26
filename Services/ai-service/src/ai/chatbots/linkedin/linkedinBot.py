from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
import asyncio
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import aioredis
from prometheus_client import Counter, Histogram, Gauge
from tenacity import retry, stop_after_attempt, wait_exponential

# Core components
from src.ai.nlp.huggingface_processor import HuggingFaceProcessor
from src.ai.queue.redis_backend import RedisQueue
from src.ai.database.sales import SalesDatabase
from src.ai.ticketing import TicketingSystem
from security.ratelimiter import RateLimiter
from utils.cache import TTLCache
from utils.logger import logger
from src.ai.decorators.retry import retry
from src.ai.decorators.background_task import background_task
from src.config import Settings

class BotConfig:
    """Centralized configuration management"""
    MAX_RETRY_ATTEMPTS = 3
    CONVERSATION_CACHE_TTL = 3600  # 1 hour
    CONVERSATION_CACHE_SIZE = 1000
    QUEUE_BATCH_SIZE = 100
    METRIC_LABELS = ['intent', 'status', 'error_type']
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

@dataclass(frozen=True)
class CustomerQuery:
    """Immutable customer query representation"""
    user_id: str
    query: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: str = "linkedin"

class ConversationState(Enum):
    """Conversation state management"""
    CONNECTING = "connecting"
    MESSAGING = "messaging"
    SALES = "sales"
    SUPPORT = "support"
    IDLE = "idle"

class InteractionType(Enum):
    """Interaction type classification"""
    SUPPORT = "support"
    SALES = "sales"
    INFO = "info"
    HANDOFF = "handoff"
    ERROR = "error"

class BotMetrics:
    """Centralized metrics management"""
    def __init__(self):
        self.interaction_counter = Counter(
            'bot_interactions_total',
            'Total number of bot interactions',
            BotConfig.METRIC_LABELS
        )
        self.response_time = Histogram(
            'bot_response_time_seconds',
            'Time taken to respond to queries',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        self.active_conversations = Gauge(
            'bot_active_conversations',
            'Number of active conversations'
        )

class ResponseHandler(ABC):
    """Abstract base class for response handling"""
    @abstractmethod
    async def handle(self, query: CustomerQuery) -> Dict[str, Any]:
        pass

    async def validate_response(self, response: Dict[str, Any]) -> bool:
        return bool(response and isinstance(response, dict))

class LinkedInBot:
    """Enhanced LinkedIn bot with advanced features"""
    def __init__(
        self,
        settings: Settings,
        nlp_processor: Optional[HuggingFaceProcessor] = None,
        sales_db: Optional[SalesDatabase] = None,
        ticketing_system: Optional[TicketingSystem] = None,
        redis_url: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None
    ):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Core components initialization
        self.nlp = nlp_processor or HuggingFaceProcessor()
        self.sales_db = sales_db or SalesDatabase()
        self.ticketing = ticketing_system or TicketingSystem()
        self.rate_limiter = rate_limiter or RateLimiter()
        
        # Performance optimization
        self.conversation_cache = TTLCache(
            maxsize=BotConfig.CONVERSATION_CACHE_SIZE,
            ttl=BotConfig.CONVERSATION_CACHE_TTL
        )
        
        # Monitoring and metrics
        self.metrics = BotMetrics()
        
        # State management
        self.redis_pool = None
        self.redis_url = redis_url
        self.conversations: Dict[str, Dict[str, Any]] = {}
        
        # Initialize async components
        self.initialization_task = asyncio.create_task(self._initialize_components())

    async def _initialize_components(self):
        """Asynchronous component initialization"""
        try:
            if self.redis_url:
                self.redis_pool = await aioredis.create_redis_pool(
                    self.redis_url,
                    minsize=5,
                    maxsize=10
                )
            await self._load_initial_state()
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            raise

    @retry(
        stop=stop_after_attempt(BotConfig.MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def handle_message(
        self,
        query: str,
        user_id: str,
        platform: str = "linkedin"
    ) -> Dict[str, Any]:
        """Main message handling with advanced error handling and metrics"""
        if not await self.initialization_task:
            raise RuntimeError("Bot initialization incomplete")

        if self.rate_limiter.is_limited(user_id):
            return {"error": "Rate limit exceeded", "retry_after": self.rate_limiter.get_retry_after(user_id)}

        with self.metrics.response_time.time():
            try:
                customer_query = CustomerQuery(
                    user_id=user_id,
                    query=query,
                    timestamp=datetime.utcnow(),
                    platform=platform
                )

                # Process query and generate response
                response = await self._process_query(customer_query)
                
                # Update metrics and state
                self._update_metrics(response["intent"], "success")
                await self._update_conversation_state(user_id, response)

                return response

            except Exception as e:
                self.logger.exception("Message handling error")
                return await self._handle_error(customer_query, str(e))

    async def cleanup(self):
        """Resource cleanup"""
        try:
            if self.redis_pool:
                self.redis_pool.close()
                await self.redis_pool.wait_closed()
            await self._save_state()
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    def _setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            format=BotConfig.LOG_FORMAT,
            level=logging.INFO
        )

    async def _process_query(self, query: CustomerQuery) -> Dict[str, Any]:
        """Process individual queries with caching"""
        cache_key = f"{query.user_id}:{query.query}"
        cached_response = self.conversation_cache.get(cache_key)
        
        if cached_response:
            return cached_response

        response = await self._generate_response(query)
        self.conversation_cache[cache_key] = response
        return response

    # Additional helper methods would go here...
