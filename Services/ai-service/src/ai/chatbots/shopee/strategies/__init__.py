"""
__init__.py
Package of strategies for the Shopee chatbot.

This module implements a clean and extensible strategy pattern for handling
different Shopee bot functionalities. All strategies are lazy-loaded to
improve performance and reduce memory usage.
"""

from typing import Dict, Type
from abc import ABC, abstractmethod
from importlib import import_module
from functools import lru_cache

class ShopeeStrategyBase(ABC):
    """Base abstract class for all Shopee bot strategies."""
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the strategy logic."""
        pass

# Lazy loading strategy mapping
STRATEGY_MAPPING: Dict[str, str] = {
    'product_search': '.product_search.ProductSearchStrategy',
    'price_comparison': '.price_comparison.PriceComparisonStrategy',
    'shipping_inquiry': '.shipping_inquiry.ShippingInquiryStrategy',
    'returns_and_refunds': '.returns_and_refunds.ReturnsAndRefundsStrategy'
}

@lru_cache(maxsize=None)
def get_strategy(strategy_name: str) -> Type[ShopeeStrategyBase]:
    """
    Lazy loads and returns the requested strategy class.
    
    Args:
        strategy_name: Name of the strategy to load
        
    Returns:
        The strategy class
        
    Raises:
        ValueError: If strategy_name is not found
    """
    if strategy_name not in STRATEGY_MAPPING:
        raise ValueError(f"Strategy '{strategy_name}' not found")
    
    module_path = STRATEGY_MAPPING[strategy_name]
    module_name, class_name = module_path.rsplit('.', 1)
    module = import_module(module_name, package=__package__)
    return getattr(module, class_name)

__all__ = [
    'ShopeeStrategyBase',
    'get_strategy',
    'STRATEGY_MAPPING'
]
