"""
handler.py
Centraliza e gerencia as estratégias do AmazonBot com recursos avançados de
tratamento de erros, validação, cache, métricas e observabilidade.
"""
from typing import Dict, Any, Optional, Type, List, Callable
from functools import lru_cache, wraps
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import logging
from datetime import datetime

from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, ValidationError

from utils.logger import logger
from .base import BaseAmazonStrategy
from .product_search import ProductSearchStrategy
from .price_comparison import PriceComparisonStrategy
from .inventory_check import InventoryCheckStrategy
from .shipping_status import ShippingStatusStrategy
from .coupons import CouponsStrategy
from .returns_and_refunds import ReturnsAndRefundsStrategy
from .recommendations import RecommendationsStrategy
from .review_analysis import ReviewAnalysisStrategy
from .order_tracking import OrderTrackingStrategy

# Métricas
STRATEGY_EXECUTION_TIME = Histogram(
    'amazon_strategy_execution_seconds',
    'Time spent executing strategy',
    ['strategy_type']
)
STRATEGY_ERRORS = Counter(
    'amazon_strategy_errors_total',
    'Total number of strategy errors',
    ['strategy_type', 'error_type']
)
ACTIVE_STRATEGIES = Gauge(
    'amazon_active_strategies',
    'Number of currently active strategies'
)

class StrategyError(Exception):
    """Exceção base para erros relacionados a estratégias."""
    def __init__(self, message: str, strategy_type: str = None):
        super().__init__(message)
        self.strategy_type = strategy_type
        self.timestamp = datetime.utcnow()

class StrategyNotFoundError(StrategyError):
    """Exceção lançada quando uma estratégia não é encontrada."""
    pass

class StrategyExecutionError(StrategyError):
    """Exceção lançada quando ocorre erro na execução da estratégia."""
    pass

class StrategyValidationError(StrategyError):
    """Exceção lançada quando falha a validação dos parâmetros da estratégia."""
    pass

class StrategyType(Enum):
    """Enum para tipos de estratégias suportadas."""
    PRODUCT_SEARCH = auto()
    PRICE_COMPARISON = auto()
    INVENTORY_CHECK = auto()
    SHIPPING_STATUS = auto()
    COUPONS = auto()
    RETURNS_AND_REFUNDS = auto()
    RECOMMENDATIONS = auto()
    REVIEW_ANALYSIS = auto()
    ORDER_TRACKING = auto()

    @classmethod
    def list(cls) -> List[str]:
        return [strategy.name.lower() for strategy in cls]

@dataclass
class StrategyContext:
    """Contexto de execução da estratégia"""
    strategy_type: StrategyType
    params: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.trace_id = trace.get_current_span().get_span_context().trace_id
        self.correlation_id = self.metadata.get('correlation_id')

def strategy_monitor(func: Callable) -> Callable:
    """Decorator para monitoramento de estratégias"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        strategy_type = args[1] if len(args) > 1 else kwargs.get('strategy_type')
        start_time = time.time()
        
        try:
            ACTIVE_STRATEGIES.inc()
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            STRATEGY_ERRORS.labels(
                strategy_type=strategy_type,
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            ACTIVE_STRATEGIES.dec()
            STRATEGY_EXECUTION_TIME.labels(
                strategy_type=strategy_type
            ).observe(time.time() - start_time)
    
    return wrapper
