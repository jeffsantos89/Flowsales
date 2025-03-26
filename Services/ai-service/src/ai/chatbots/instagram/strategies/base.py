from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from logging import Logger, getLogger, basicConfig
from datetime import datetime
from dataclasses import dataclass, field
import asyncio
from enum import Enum
from contextlib import asynccontextmanager

# Configure logging with best practices
basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class MessageType(Enum):
    """Enumeration for different types of messages"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"

@dataclass(frozen=True)
class MessageContext:
    """Immutable data class for message context"""
    user_id: str
    message_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    content: str = ""
    message_type: MessageType = MessageType.TEXT
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate message context after initialization"""
        if not self.user_id or not self.message_id:
            raise ValueError("user_id and message_id are required")

class InstagramStrategyException(Exception):
    """Base exception for Instagram strategy errors"""
    pass

class ConfigValidationError(InstagramStrategyException):
    """Configuration validation specific exception"""
    pass

class ProcessingError(InstagramStrategyException):
    """Message processing specific exception"""
    pass

class BaseInstagramStrategy(ABC):
    """Enhanced abstract base class for Instagram chatbot strategies"""

    def __init__(
        self, 
        config: Dict[str, Any], 
        logger: Optional[Logger] = None,
        retry_policy: Optional[Dict[str, Any]] = None
    ):
        self.config = config
        self.logger = logger or getLogger(self.__class__.__name__)
        self._setup_retry_policy(retry_policy)
        self._initialize()

    def _setup_retry_policy(self, retry_policy: Optional[Dict[str, Any]]) -> None:
        """Configure retry mechanism"""
        default_policy = {
            'max_retries': 3,
            'retry_delay': 1.0,
            'exponential_backoff': True,
            'max_delay': 30.0
        }
        self.retry_policy = {**default_policy, **(retry_policy or {})}

    def _initialize(self) -> None:
        """Initialize strategy with enhanced error handling"""
        try:
            self.validate_config()
            self.logger.info(
                f"Initialized {self.__class__.__name__} strategy with config: {self.config}"
            )
        except Exception as e:
            self.logger.critical(f"Critical initialization error: {str(e)}")
            raise ConfigValidationError(f"Initialization failed: {str(e)}") from e

    @abstractmethod
    def validate_config(self) -> None:
        """Validate strategy configuration"""
        pass

    @abstractmethod
    async def process_message(self, context: MessageContext) -> Dict[str, Any]:
        """Process incoming message"""
        pass

    async def _calculate_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff"""
        if self.retry_policy['exponential_backoff']:
            delay = self.retry_policy['retry_delay'] * (2 ** attempt)
            return min(delay, self.retry_policy['max_delay'])
        return self.retry_policy['retry_delay']

    async def execute(self, context: MessageContext) -> Dict[str, Any]:
        """Execute strategy with enhanced retry mechanism"""
        last_exception = None

        for attempt in range(self.retry_policy['max_retries']):
            try:
                self.logger.debug(
                    f"Processing message {context.message_id}, attempt {attempt + 1}"
                )
                return await self.process_message(context)

            except Exception as e:
                last_exception = e
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}",
                    exc_info=True
                )
                
                if attempt < self.retry_policy['max_retries'] - 1:
                    delay = await self._calculate_delay(attempt)
                    self.logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)

        self.logger.error(
            f"All attempts failed for message {context.message_id}",
            exc_info=last_exception
        )
        raise ProcessingError(
            f"Processing failed after {self.retry_policy['max_retries']} attempts"
        ) from last_exception

    @asynccontextmanager
    async def managed_execution(self, context: MessageContext):
        """Context manager for safe strategy execution"""
        try:
            yield await self.execute(context)
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Enhanced cleanup with proper resource management"""
        try:
            self.logger.info(f"Cleaning up {self.__class__.__name__} resources")
            await self._cleanup_implementation()
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}", exc_info=True)
            raise InstagramStrategyException(f"Cleanup failed: {str(e)}") from e

    async def _cleanup_implementation(self) -> None:
        """Implementation specific cleanup"""
        pass

    def __repr__(self) -> str:
        """Enhanced string representation"""
        return (
            f"{self.__class__.__name__}("
            f"config={self.config}, "
            f"retry_policy={self.retry_policy})"
        )
