"""
shipping_inquiry.py
Strategy for handling shipping inquiries (freight, delivery time, status).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShippingQueryType(Enum):
    DELIVERY_TIME = "delivery_time"
    SHIPPING_COST = "shipping_cost"
    TRACKING_STATUS = "tracking_status"
    GENERAL = "general"

@dataclass
class ShippingQuery:
    user_id: str
    message: str
    query_type: ShippingQueryType
    tracking_number: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None

class ShippingResponseBuilder:
    @staticmethod
    def build_response(query_type: ShippingQueryType, data: Dict[str, Any]) -> str:
        responses = {
            ShippingQueryType.DELIVERY_TIME: "O prazo de envio na Shopee varia de 2 a 10 dias úteis, dependendo da localização do vendedor e do método de envio escolhido.",
            ShippingQueryType.SHIPPING_COST: "O custo do frete é calculado com base na localização, peso e dimensões do produto.",
            ShippingQueryType.TRACKING_STATUS: f"Para rastrear seu pedido, utilize o número de rastreio: {data.get('tracking_number', 'Não disponível')}",
            ShippingQueryType.GENERAL: "Como posso ajudar com suas dúvidas sobre envio?"
        }
        return responses.get(query_type, responses[ShippingQueryType.GENERAL])

class ShippingInquiryStrategy:
    """
    Handles shipping queries on Shopee, such as delivery times, shipping costs, and tracking status.
    """

    def __init__(self):
        self._query_analyzer = ShippingQueryAnalyzer()
        self._response_builder = ShippingResponseBuilder()

    def execute(self, user_id: str, message_text: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the shipping inquiry strategy.
        
        Args:
            user_id: The user's identifier
            message_text: The user's message
            query_info: Additional query information
            
        Returns:
            Dict containing the response and strategy information
        """
        try:
            logger.info(f"Processing shipping inquiry for user_id={user_id}")
            
            # Analyze the query
            query_type = self._query_analyzer.analyze(message_text)
            
            # Create shipping query object
            query = ShippingQuery(
                user_id=user_id,
                message=message_text,
                query_type=query_type,
                additional_info=query_info
            )
            
            # Build response
            response = self._response_builder.build_response(query_type, query_info)
            
            return {
                "response": response,
                "strategy": "shipping_inquiry",
                "query_type": query_type.value,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing shipping inquiry: {str(e)}", exc_info=True)
            return {
                "response": "Desculpe, não foi possível processar sua consulta no momento. Tente novamente mais tarde.",
                "strategy": "shipping_inquiry",
                "status": "error",
                "error": str(e)
            }

class ShippingQueryAnalyzer:
    """
    Analyzes shipping queries to determine their type.
    """
    
    def analyze(self, message: str) -> ShippingQueryType:
        message = message.lower()
        
        if any(word in message for word in ["prazo", "quando chega", "tempo"]):
            return ShippingQueryType.DELIVERY_TIME
        elif any(word in message for word in ["frete", "custo", "valor envio"]):
            return ShippingQueryType.SHIPPING_COST
        elif any(word in message for word in ["rastreio", "rastrear", "status"]):
            return ShippingQueryType.TRACKING_STATUS
        
        return ShippingQueryType.GENERAL
