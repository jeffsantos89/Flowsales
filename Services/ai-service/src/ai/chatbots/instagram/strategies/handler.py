from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import asyncio
from dataclasses import dataclass
from enum import Enum
import traceback
from contextlib import asynccontextmanager

# Advanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    STORY = "story"
    VOICE = "voice"
    INTERACTIVE = "interactive"
    LOCATION = "location"
    DOCUMENT = "document"

@dataclass(frozen=True)
class Message:
    """Immutable message representation with enhanced validation"""
    content: Any
    message_type: MessageType
    sender_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.sender_id:
            raise ValueError("sender_id cannot be empty")
        if not isinstance(self.timestamp, datetime):
            object.__setattr__(self, 'timestamp', datetime.fromisoformat(self.timestamp))
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})

class StrategyResult:
    """Enhanced result class with validation and metadata"""
    def __init__(
        self, 
        success: bool, 
        response: Any = None, 
        error: Optional[Exception] = None,
        metadata: Dict[str, Any] = None
    ):
        self.success = success
        self.response = response
        self.error = error
        self.timestamp = datetime.utcnow()
        self.metadata = metadata or {}

    def __repr__(self):
        return (f"StrategyResult(success={self.success}, "
                f"response={self.response}, error={self.error}, "
                f"timestamp={self.timestamp.isoformat()})")

class StrategyError(Exception):
    """Custom exception for strategy-related errors"""
    pass

MiddlewareFunc = Callable[[Any, str], asyncio.coroutine]

class BaseStrategy(ABC):
    """Enhanced base strategy with lifecycle methods"""
    
    async def initialize(self) -> None:
        """Initialize strategy resources"""
        pass
    
    @abstractmethod
    async def execute(self, message: Message) -> StrategyResult:
        """Process the message"""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup strategy resources"""
        pass
    
    async def validate(self, message: Message) -> bool:
        """Validate if message can be processed by this strategy"""
        return True

class StrategyHandler:
    """Enhanced Strategy Handler with advanced features"""
    
    def __init__(self):
        self._strategies: Dict[str, BaseStrategy] = {}
        self._fallback_strategy: Optional[BaseStrategy] = None
        self._middleware: List[MiddlewareFunc] = []
        self._active = False
    
    @asynccontextmanager
    async def lifecycle(self):
        """Context manager for handler lifecycle"""
        await self.startup()
        try:
            yield self
        finally:
            await self.shutdown()
    
    async def startup(self):
        """Initialize handler and all strategies"""
        if self._active:
            return
        
        logger.info("Starting StrategyHandler")
        for name, strategy in self._strategies.items():
            try:
                await strategy.initialize()
                logger.info(f"Initialized strategy: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize strategy {name}: {e}")
                raise
        
        self._active = True

    async def shutdown(self):
        """Cleanup handler and all strategies"""
        if not self._active:
            return
        
        logger.info("Shutting down StrategyHandler")
        for name, strategy in self._strategies.items():
            try:
                await strategy.cleanup()
                logger.info(f"Cleaned up strategy: {name}")
            except Exception as e:
                logger.error(f"Error cleaning up strategy {name}: {e}")
        
        self._active = False

    def register_strategy(self, name: str, strategy: BaseStrategy) -> None:
        if not isinstance(strategy, BaseStrategy):
            raise ValueError("Strategy must inherit from BaseStrategy")
        self._strategies[name] = strategy
        logger.info(f"Strategy '{name}' registered successfully")

    def register_middleware(self, middleware_func: MiddlewareFunc) -> None:
        self._middleware.append(middleware_func)

    def set_fallback_strategy(self, strategy: BaseStrategy) -> None:
        self._fallback_strategy = strategy

    async def _execute_middleware(self, data: Any, direction: str) -> Any:
        current_data = data
        for mw in self._middleware:
            try:
                current_data = await mw(current_data, direction)
            except Exception as e:
                logger.error(f"Middleware error: {str(e)}")
                raise StrategyError(f"Middleware failure: {str(e)}")
        return current_data

    async def handle_message(self, message: Message, strategy_name: Optional[str] = None) -> StrategyResult:
        if not self._active:
            raise RuntimeError("StrategyHandler not started. Use 'lifecycle' context manager.")
        
        try:
            message = await self._execute_middleware(message, "incoming")
            
            strategy = self._strategies.get(strategy_name)
            if not strategy:
                if self._fallback_strategy:
                    strategy = self._fallback_strategy
                    logger.warning(f"Using fallback strategy for message from {message.sender_id}")
                else:
                    raise StrategyError(f"No strategy found for '{strategy_name}' and no fallback defined")

            if not await strategy.validate(message):
                raise StrategyError(f"Message validation failed for strategy {strategy_name}")

            result = await strategy.execute(message)

            if result.success and result.response:
                result.response = await self._execute_middleware(result.response, "outgoing")

            return result

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}\n{traceback.format_exc()}")
            return StrategyResult(success=False, error=e)

    async def handle_batch_messages(
        self, 
        messages: List[Message], 
        strategy_name: Optional[str] = None,
        batch_size: int = 10
    ) -> List[StrategyResult]:
        """Process messages in batches for better resource management"""
        results = []
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            tasks = [self.handle_message(msg, strategy_name) for msg in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
        return results

    def get_available_strategies(self) -> List[str]:
        return list(self._strategies.keys())
