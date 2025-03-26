from typing import Dict, Any, Optional, List, Type
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum, auto
import structlog
from opentelemetry import trace, metrics
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, validator, Field
from contextlib import contextmanager, asynccontextmanager
import asyncio
from functools import wraps
from abc import ABC, abstractmethod

# Core service imports
from ai.nlp.huggingface_processor import HuggingFaceProcessor
from ai.queue.redis_backend import RedisQueue
from ai.database.sales import SalesDatabase
from ai.ticketing import TicketingSystem
from security.ratelimiter import RateLimiter
from utils.cache import TTLCache
from utils.logger import logger

# Strategy imports
from ai.chatbots.mercadolivre.strategies import (
    BaseStrategy,
    ProductSearchStrategy,
    PriceComparisonStrategy, 
    ShippingInquiryStrategy,
    ReturnsAndRefundsStrategy,
    StockAndNegotiationStrategy,
    ProductRecommendationStrategy,
    ProductDetailsStrategy
)
from ai.chatbots.mercadolivre.query import MercadoLibreQueryPipeline
from database.inventory import InventoryDatabase

class Config:
    """Advanced configuration with environment variable support and validation"""
    from environs import Env
    env = Env()
    
    class Settings(BaseModel):
        MAX_RETRIES: int = Field(default=3, ge=1)
        TIMEOUT_SECONDS: int = Field(default=10, ge=1)
        BATCH_SIZE: int = Field(default=100, ge=1)
        CACHE_TTL: int = Field(default=3600, ge=0)
        RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1)
        RATE_LIMIT_WINDOW: int = Field(default=60, ge=1)
        CIRCUIT_BREAKER_THRESHOLD: float = Field(default=0.5, ge=0, le=1)
        CIRCUIT_BREAKER_RECOVERY_TIME: int = Field(default=30, ge=1)
        
    @classmethod
    def load(cls) -> Settings:
        return cls.Settings(
            MAX_RETRIES=cls.env.int("MAX_RETRIES", 3),
            TIMEOUT_SECONDS=cls.env.int("TIMEOUT_SECONDS", 10),
            BATCH_SIZE=cls.env.int("BATCH_SIZE", 100),
            CACHE_TTL=cls.env.int("CACHE_TTL", 3600),
            RATE_LIMIT_REQUESTS=cls.env.int("RATE_LIMIT_REQUESTS", 100),
            RATE_LIMIT_WINDOW=cls.env.int("RATE_LIMIT_WINDOW", 60),
            CIRCUIT_BREAKER_THRESHOLD=cls.env.float("CIRCUIT_BREAKER_THRESHOLD", 0.5),
            CIRCUIT_BREAKER_RECOVERY_TIME=cls.env.int("CIRCUIT_BREAKER_RECOVERY_TIME", 30)
        )

class ConversationState(Enum):
    """Enhanced conversation state tracking with state transitions"""
    INITIAL = "initial"
    PRODUCT = "product"
    PRICE = "price" 
    SHIPPING = "shipping"
    RETURNS = "returns"
    NEGOTIATION = "negotiation"
    IDLE = "idle"
    CLOSED = "closed"
    
    def can_transition_to(self, new_state: 'ConversationState') -> bool:
        transitions = {
            self.INITIAL: [self.PRODUCT, self.PRICE, self.SHIPPING],
            self.PRODUCT: [self.PRICE, self.SHIPPING, self.NEGOTIATION],
            self.PRICE: [self.SHIPPING, self.NEGOTIATION, self.CLOSED],
            self.SHIPPING: [self.RETURNS, self.CLOSED],
            self.RETURNS: [self.CLOSED],
            self.NEGOTIATION: [self.CLOSED],
            self.IDLE: [self.INITIAL],
            self.CLOSED: [self.INITIAL]
        }
        return new_state in transitions.get(self, [])

class CustomerIntent(Enum):
    """Enhanced customer intent classification with confidence scores"""
    COMPLAINT = auto()
    SHIPPING = auto()
    RETURN_REFUND = auto()
    TECHNICAL_SUPPORT = auto()
    URGENT_HELP = auto()
    SALES = auto()
    NEGOTIATION = auto()
    STOCK = auto()
    GENERAL = auto()

    @classmethod
    def from_str(cls, intent_str: str, confidence: float = 0.0) -> tuple['CustomerIntent', float]:
        intent = cls.__members__.get(intent_str.upper(), cls.GENERAL)
        return intent, confidence

class ProcessingStatus(Enum):
    """Enhanced processing status with detailed states and handling recommendations"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    CACHED = "cached"
    INVALID_REQUEST = "invalid_request"
    CIRCUIT_BROKEN = "circuit_broken"
    
    @property
    def should_retry(self) -> bool:
        return self in {self.ERROR, self.TIMEOUT, self.RATE_LIMITED}

class MessagePriority(Enum):
    """Message priority levels with SLA hints and handling strategies"""
    URGENT = "urgent"   # Response within 30 seconds
    HIGH = "high"      # Response within 1 minute
    MEDIUM = "medium"  # Response within 5 minutes
    LOW = "low"        # Response within 15 minutes
    
    @property
    def sla_seconds(self) -> int:
        sla_map = {
            self.URGENT: 30,
            self.HIGH: 60,
            self.MEDIUM: 300,
            self.LOW: 900
        }
        return sla_map[self]

@dataclass
class ProcessingResult:
    """Enhanced processing result with validation, metrics and error handling"""
    intent: str
    response: Dict
    status: ProcessingStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.MEDIUM
    processing_time: float = 0.0
    customer_id: str = field(default="anonymous")
    confidence_score: float = field(default=0.0)
    error_details: Optional[Dict] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "response": self.response,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "priority": self.priority.value,
            "processing_time": self.processing_time,
            "customer_id": self.customer_id,
            "confidence_score": self.confidence_score,
            "error_details": self.error_details
        }

    @property
    def is_successful(self) -> bool:
        return self.status == ProcessingStatus.SUCCESS

class MessageRequest(BaseModel):
    """Enhanced message request with validation and metadata"""
    content: str
    customer_id: str
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: MessagePriority = Field(default=MessagePriority.MEDIUM)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = Field(default=None)
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    class Config:
        validate_assignment = True
        extra = "forbid"

class MercadoLivreChatBot:
    """Production-ready MercadoLivre ChatBot with advanced features and robust error handling"""

    def __init__(
        self,
        nlp_processor: Optional[HuggingFaceProcessor] = None,
        sales_db: Optional[SalesDatabase] = None,
        ticketing: Optional[TicketingSystem] = None,
        queue: Optional[RedisQueue] = None,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[TTLCache] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = Config.load()
        self._setup_services(
            nlp_processor or HuggingFaceProcessor(),
            sales_db or SalesDatabase(),
            ticketing or TicketingSystem(),
            queue or RedisQueue(),
            rate_limiter or RateLimiter(),
            cache or TTLCache()
        )
        
        self._setup_metrics()
        self._setup_logging()
        self._setup_strategies()
        
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.query_pipeline = MercadoLibreQueryPipeline(self.nlp_service)
        self._running = False
        
        # Telemetry
        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)

    def _setup_services(self, *args):
        """Initialize core services"""
        (
            self.nlp_service,
            self.sales_db,
            self.ticketing,
            self.queue,
            self.rate_limiter,
            self.cache
        ) = args
        
    def _setup_strategies(self):
        """Initialize conversation strategies with dependency injection"""
        inventory_db = InventoryDatabase()
        
        self.strategies = {
            "product_search": ProductSearchStrategy(self.nlp_service, self.sales_db),
            "price_comparison": PriceComparisonStrategy(self.sales_db),
            "shipping_inquiry": ShippingInquiryStrategy(),
            "returns": ReturnsAndRefundsStrategy(self.ticketing),
            "stock_negotiation": StockAndNegotiationStrategy(
                inventory_db=inventory_db,
                sales_db=self.sales_db
            ),
            "product_recommendation": ProductRecommendationStrategy(self.sales_db),
            "product_details": ProductDetailsStrategy(self.sales_db)
        }

    # ... (resto do código permanece o mesmo, mas com as melhorias já implementadas)
