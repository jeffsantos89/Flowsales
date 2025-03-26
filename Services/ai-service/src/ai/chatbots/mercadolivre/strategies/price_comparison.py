"""
price_comparison.py
Estratégia para comparar preços de um produto no Mercado Livre ou concorrentes.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from enum import Enum
from ai.database.sales import SalesDatabase
from ai.exceptions import ProductNotFoundError, InvalidProductIdError

logger = logging.getLogger(__name__)

@dataclass
class PriceData:
    """Estrutura de dados para informações de preço"""
    seller_id: str
    price: float
    condition: str
    last_updated: datetime
    shipping_cost: float
    total_price: float
    availability: int
    rating: float

class PriceComparisonStatus(Enum):
    SUCCESS = "success"
    PRODUCT_NOT_FOUND = "product_not_found"
    INVALID_PRODUCT = "invalid_product"
    ERROR = "error"

class PriceExtractor(ABC):
    """Interface para diferentes estratégias de extração de product_id"""
    @abstractmethod
    def extract_product_id(self, query_info: Dict[str, Any]) -> Optional[str]:
        pass

class MLPriceExtractor(PriceExtractor):
    """Implementação específica para Mercado Livre"""
    def extract_product_id(self, query_info: Dict[str, Any]) -> Optional[str]:
        try:
            if "entities" in query_info and "product_id" in query_info["entities"]:
                return query_info["entities"]["product_id"]
            return None
        except Exception as e:
            logger.error(f"Error extracting product_id: {str(e)}")
            return None

class PriceComparisonStrategy:
    """
    Compara preços de um determinado produto em diferentes sellers.
    """

    def __init__(self, sales_db: SalesDatabase, price_extractor: PriceExtractor = None):
        self.sales_db = sales_db
        self.price_extractor = price_extractor or MLPriceExtractor()
        self.min_confidence_threshold = 0.7

    async def execute(self, user_id: str, query_text: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a comparação de preços de forma assíncrona
        """
        logger.info(f"[PriceComparisonStrategy] Initiating price comparison for user_id={user_id}")
        
        try:
            product_id = self._validate_product_id(
                self.price_extractor.extract_product_id(query_info)
            )
            
            if not product_id:
                return self._build_response(
                    status=PriceComparisonStatus.INVALID_PRODUCT,
                    message="Qual produto você gostaria de comparar?"
                )

            price_data = await self._get_price_comparison(product_id)
            
            return self._build_response(
                status=PriceComparisonStatus.SUCCESS,
                message="Aqui está a comparação de preços:",
                data=self._process_price_data(price_data)
            )

        except ProductNotFoundError:
            return self._build_response(
                status=PriceComparisonStatus.PRODUCT_NOT_FOUND,
                message="Produto não encontrado."
            )
        except Exception as e:
            logger.error(f"Error in price comparison: {str(e)}", exc_info=True)
            return self._build_response(
                status=PriceComparisonStatus.ERROR,
                message="Desculpe, ocorreu um erro ao comparar os preços."
            )

    def _validate_product_id(self, product_id: Optional[str]) -> Optional[str]:
        """Valida o formato do product_id"""
        if not product_id:
            return None
        if not isinstance(product_id, str) or len(product_id) < 5:
            raise InvalidProductIdError(f"Invalid product_id format: {product_id}")
        return product_id

    async def _get_price_comparison(self, product_id: str) -> List[PriceData]:
        """Obtém dados de preço do banco de dados"""
        price_data = await self.sales_db.compare_prices(product_id)
        if not price_data:
            raise ProductNotFoundError(f"No price data found for product {product_id}")
        return price_data

    def _process_price_data(self, price_data: List[PriceData]) -> Dict[str, Any]:
        """Processa e organiza os dados de preço"""
        return {
            "lowest_price": min(p.total_price for p in price_data),
            "highest_price": max(p.total_price for p in price_data),
            "average_price": sum(p.total_price for p in price_data) / len(price_data),
            "seller_count": len(price_data),
            "prices": [self._format_price_data(p) for p in price_data]
        }

    def _format_price_data(self, price: PriceData) -> Dict[str, Any]:
        """Formata os dados de preço para resposta"""
        return {
            "seller_id": price.seller_id,
            "price": price.price,
            "shipping": price.shipping_cost,
            "total": price.total_price,
            "condition": price.condition,
            "availability": price.availability,
            "rating": price.rating,
            "last_updated": price.last_updated.isoformat()
        }

    def _build_response(self, status: PriceComparisonStatus, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Constrói a resposta padronizada"""
        response = {
            "status": status.value,
            "message": message,
            "strategy": "price_comparison",
            "timestamp": datetime.utcnow().isoformat()
        }
        if data:
            response["data"] = data
        return response
