"""
__init__.py
Este módulo inicializa o pacote de estratégias para o chatbot do Mercado Livre.
Fornece um sistema modular e extensível para diferentes funcionalidades de interação.

Attributes:
    __version__ (str): Versão atual do módulo
    __author__ (str): Autor do módulo
    AVAILABLE_STRATEGIES (dict): Mapeamento de todas as estratégias disponíveis
"""

from typing import Dict, Type
from abc import ABC
import logging
from pathlib import Path

# Importação das estratégias
from .product_search import ProductSearchStrategy
from .price_comparison import PriceComparisonStrategy
from .shipping_inquiry import ShippingInquiryStrategy
from .returns_and_refunds import ReturnsAndRefundsStrategy

# Configuração de logging
logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Flowsale Team"

# Mapeamento de estratégias disponíveis
AVAILABLE_STRATEGIES: Dict[str, Type[ABC]] = {
    "product_search": ProductSearchStrategy,
    "price_comparison": PriceComparisonStrategy,
    "shipping_inquiry": ShippingInquiryStrategy,
    "returns_and_refunds": ReturnsAndRefundsStrategy
}

def get_strategy(strategy_name: str) -> Type[ABC]:
    """
    Recupera uma estratégia específica pelo nome.
    
    Args:
        strategy_name (str): Nome da estratégia desejada
        
    Returns:
        Type[ABC]: Classe da estratégia
        
    Raises:
        KeyError: Se a estratégia não existir
    """
    try:
        return AVAILABLE_STRATEGIES[strategy_name]
    except KeyError:
        logger.error(f"Estratégia não encontrada: {strategy_name}")
        raise KeyError(f"Estratégia '{strategy_name}' não está disponível")

def list_available_strategies() -> list:
    """
    Lista todas as estratégias disponíveis.
    
    Returns:
        list: Lista com os nomes das estratégias disponíveis
    """
    return list(AVAILABLE_STRATEGIES.keys())

# Expose public interface
__all__ = [
    "ProductSearchStrategy",
    "PriceComparisonStrategy",
    "ShippingInquiryStrategy",
    "ReturnsAndRefundsStrategy",
    "get_strategy",
    "list_available_strategies",
    "AVAILABLE_STRATEGIES"
]
