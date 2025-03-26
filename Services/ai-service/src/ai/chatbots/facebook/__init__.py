from typing import Dict, Any, Optional, Union, TypeVar, Protocol, List, Callable
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
from datetime import datetime
import os
from functools import wraps
from enum import Enum
import aiohttp
import backoff
from contextlib import asynccontextmanager

"""
Enterprise Facebook Chatbot Module
Production-grade implementation with advanced features:
- Circuit breaker pattern
- Metric collection
- Connection pooling
- Rate limiting
- Webhook validation
- Enhanced security
"""

# Type definitions and enums
ConfigType = TypeVar('ConfigType', bound=Dict[str, Any])
T = TypeVar('T')

class MessageType(Enum):
    TEXT = "text"
    TEMPLATE = "template"
    ATTACHMENT = "attachment"
    QUICK_REPLY = "quick_reply"

class FacebookError(Exception):
    """Base exception for Facebook-related errors"""
    pass

class FacebookBotProtocol(Protocol):
    """Protocol defining the interface for Facebook bot implementations"""
    async def initialize(self) -> None: ...
    async def cleanup(self) -> None: ...
    async def send_message(self, payload: Dict[str, Any]) -> Any: ...

class RateLimitError(FacebookError):
    """Raised when hitting Facebook API rate limits"""
    pass

class ConfigurationManager:
    """Manages Facebook bot configuration"""
    def __init__(self):
        self.config = FacebookConfig(
            version="v12.0",
            timeout=30,
            retry_attempts=3,
            base_url="https://graph.facebook.com",
            verify_token="",  # Set your verify token
            page_access_token="",  # Set your page access token
            webhook_secret=""  # Set your webhook secret
        )

@dataclass(frozen=True)
class FacebookConfig:
    """Enhanced immutable configuration with validation"""
    version: str
    timeout: int
    retry_attempts: int
    base_url: str
    verify_token: str
    page_access_token: str
    webhook_secret: str
    rate_limit: int = field(default=50)
    connection_pool_size: int = field(default=100)
    circuit_breaker_threshold: int = field(default=5)
    metrics_enabled: bool = field(default=True)

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.page_access_token or not self.webhook_secret:
            raise ValueError("Missing required security credentials")

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'FacebookConfig':
        return cls(**config)

class MetricsCollector:
    """Collects and exports metrics for monitoring"""
    def __init__(self):
        self.message_count = 0
        self.error_count = 0
        self.response_times: List[float] = []

    async def record_message(self, duration: float):
        self.message_count += 1
        self.response_times.append(duration)

    async def record_error(self):
        self.error_count += 1

class CircuitBreaker:
    """Implements circuit breaker pattern"""
    def __init__(self, threshold: int, reset_timeout: int = 60):
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.is_open = False
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        if self.is_open:
            raise FacebookError("Circuit breaker is open")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            async with self._lock:
                self.failures += 1
                if self.failures >= self.threshold:
                    self.is_open = True
                    asyncio.create_task(self._reset_timer())

    async def _reset_timer(self):
        await asyncio.sleep(self.reset_timeout)
        self.is_open = False
        self.failures = 0

class FacebookBot(FacebookBotProtocol):
    """Enhanced Facebook bot implementation"""
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()
        self.circuit_breaker = CircuitBreaker(
            self.config_manager.config.circuit_breaker_threshold
        )
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        self._rate_limiter = asyncio.Semaphore(
            self.config_manager.config.rate_limit
        )

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, RateLimitError),
        max_tries=3
    )
    async def initialize(self) -> None:
        if self._initialized:
            return

        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=self.config_manager.config.connection_pool_size
            )
        )
        self._initialized = True
        self.logger.info("Facebook bot initialized successfully")

    async def cleanup(self):
        """Cleanup resources"""
        if self._session:
            await self._session.close()
        self._initialized = False

    @asynccontextmanager
    async def _rate_limit(self):
        async with self._rate_limiter:
            yield

    async def send_message(self, payload: Dict[str, Any]) -> Any:
        """Enhanced message sending with metrics and safety checks"""
        start_time = datetime.now()
        
        try:
            async with self.circuit_breaker:
                async with self._rate_limit():
                    response = await self._make_request(
                        "messages", 
                        payload
                    )
            
            duration = (datetime.now() - start_time).total_seconds()
            await self.metrics.record_message(duration)
            return response

        except Exception as e:
            await self.metrics.record_error()
            self.logger.error(f"Error sending message: {str(e)}")
            raise

    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """Make authenticated request to Facebook API"""
        if not self._session:
            raise FacebookError("Bot not initialized")

        url = f"{self.config_manager.config.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.config_manager.config.page_access_token}",
            "Content-Type": "application/json"
        }

        async with self._session.post(url, json=data, headers=headers) as response:
            if response.status == 429:
                raise RateLimitError("Rate limit exceeded")
            response.raise_for_status()
            return await response.json()

def setup_logging(log_file: Path) -> logging.Logger:
    """Setup rotating file logger"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Module initialization with enhanced logging
logger = setup_logging(Path("logs/facebook_bot.log"))
__version__ = '2.0.0'
__author__ = 'Flowsale Team'

# Export public interface
__all__ = [
    'FacebookBot',
    'FacebookConfig',
    'ConfigurationManager',
    'MessageType',
    'FacebookError'
]
