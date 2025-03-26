# src/ai/chatbots/amazon/strategies/__init__.py

from typing import Dict, Any, Type, Optional
from abc import ABC, abstractmethod
from typing import Protocol
from enum import Enum, auto
import logging
from functools import wraps
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyError(Exception):
    """Base exception for strategy-related errors."""
    pass

class StrategyNotFoundError(StrategyError):
    """Raised when a requested strategy is not found."""
    pass

class StrategyExecutionError(StrategyError):
    """Raised when strategy execution fails."""
    pass

class StrategyType(Enum):
    """Enum for different types of strategies"""
    PRODUCT_SEARCH = auto()
    PRICE_COMPARISON = auto()

def strategy_execution_timer(func):
    """Decorator to measure strategy execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Strategy {func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            logger.error(f"Strategy execution failed: {str(e)}")
            raise StrategyExecutionError(f"Strategy execution failed: {str(e)}")
    return wrapper

class AmazonStrategyBase(ABC):
    """Abstract base class for Amazon strategies"""
    
    @abstractmethod
    @strategy_execution_timer
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Base method for all Amazon strategies."""
        pass

    @abstractmethod
    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate the context before execution."""
        pass

class AmazonStrategyProtocol(Protocol):
    """Strategy protocol for type hinting."""
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]: ...
    def validate_context(self, context: Dict[str, Any]) -> bool: ...

class AmazonStrategyFactory:
    """Factory class for creating and managing Amazon strategies"""
    
    _strategies: Dict[StrategyType, Type[AmazonStrategyBase]] = {}
    _instances: Dict[StrategyType, AmazonStrategyBase] = {}
    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """Initialize the factory if not already initialized"""
        if not cls._initialized:
            from .product_search import ProductSearchStrategy
            from .price_comparison import PriceComparisonStrategy
            
            cls.register(StrategyType.PRODUCT_SEARCH, ProductSearchStrategy)
            cls.register(StrategyType.PRICE_COMPARISON, PriceComparisonStrategy)
            cls._initialized = True

    @classmethod
    def register(cls, strategy_type: StrategyType, strategy_class: Type[AmazonStrategyBase]) -> None:
        """Register a new strategy class"""
        if not issubclass(strategy_class, AmazonStrategyBase):
            raise StrategyError(f"Strategy {strategy_class.__name__} must inherit from AmazonStrategyBase")
        cls._strategies[strategy_type] = strategy_class
        logger.info(f"Strategy {strategy_class.__name__} registered successfully")

    @classmethod
    def get_strategy(cls, strategy_type: StrategyType) -> AmazonStrategyBase:
        """Get or create a strategy instance"""
        if not cls._initialized:
            cls.initialize()

        if strategy_type not in cls._strategies:
            raise StrategyNotFoundError(f"Strategy {strategy_type} not found")

        # Implement singleton pattern for strategy instances
        if strategy_type not in cls._instances:
            strategy_class = cls._strategies[strategy_type]
            cls._instances[strategy_type] = strategy_class()
            logger.debug(f"Created new instance of {strategy_class.__name__}")

        return cls._instances[strategy_type]

    @classmethod
    def clear_instances(cls) -> None:
        """Clear all strategy instances"""
        cls._instances.clear()
        logger.debug("Cleared all strategy instances")

    @classmethod
    def get_available_strategies(cls) -> Dict[StrategyType, str]:
        """Get all available strategies"""
        if not cls._initialized:
            cls.initialize()
        return {st_type: st_class.__name__ for st_type, st_class in cls._strategies.items()}

__all__ = [
    "AmazonStrategyBase",
    "AmazonStrategyProtocol",
    "AmazonStrategyFactory",
    "StrategyType",
    "StrategyError",
    "StrategyNotFoundError",
    "StrategyExecutionError"
]