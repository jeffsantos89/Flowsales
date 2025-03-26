from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import logging
from enum import Enum
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Priority(Enum):
    LOW = 1
    NORMAL = 2
    URGENT = 3

class QueryType(Enum):
    ORDER = "order"
    PRODUCT = "product"
    GENERAL = "general"

@dataclass(frozen=True)
class CustomerQuery:
    """Immutable data class representing a customer support query"""
    user_id: str
    message: str
    timestamp: datetime
    context: Dict[str, Any]
    priority: Priority = Priority.LOW

    def __post_init__(self):
        if not self.user_id or not self.message:
            raise ValueError("user_id and message are required fields")

class SupportResponse:
    """Class to handle support responses with validation"""
    def __init__(self, message: str, action_type: str, metadata: Optional[Dict] = None):
        if not message:
            raise ValueError("Response message cannot be empty")
        self.message = message
        self.action_type = action_type
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize response to dictionary"""
        return {
            "message": self.message,
            "action_type": self.action_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

class SupportStrategy(ABC):
    """Abstract base class for support strategies with common utilities"""
    @abstractmethod
    def handle_query(self, query: CustomerQuery) -> SupportResponse:
        pass

    def _log_strategy_execution(self, query: CustomerQuery) -> None:
        logger.info(
            f"[{self.__class__.__name__}] Processing query for user={query.user_id} "
            f"priority={query.priority.name}"
        )

class OrderSupportStrategy(SupportStrategy):
    def handle_query(self, query: CustomerQuery) -> SupportResponse:
        self._log_strategy_execution(query)
        # Add sophisticated order handling logic here
        return SupportResponse(
            message="Entendi sua dúvida sobre o pedido. Como posso ajudar?",
            action_type="order_support",
            metadata={"query_priority": query.priority.value}
        )

class ProductSupportStrategy(SupportStrategy):
    def handle_query(self, query: CustomerQuery) -> SupportResponse:
        self._log_strategy_execution(query)
        # Add sophisticated product handling logic here
        return SupportResponse(
            message="Posso ajudar com informações sobre nossos produtos.",
            action_type="product_support",
            metadata={"query_priority": query.priority.value}
        )

class GeneralSupportStrategy(SupportStrategy):
    def handle_query(self, query: CustomerQuery) -> SupportResponse:
        self._log_strategy_execution(query)
        # Add sophisticated general support logic here
        return SupportResponse(
            message="Como posso ajudar você hoje?",
            action_type="general_support",
            metadata={"query_priority": query.priority.value}
        )

class InstagramSupportHandler:
    """Production-ready Instagram support handler with caching and error handling"""
    
    def __init__(self):
        self._query_queue: List[CustomerQuery] = []
        self._response_cache: Dict[str, SupportResponse] = {}
        self._initialize_handlers()

    def _initialize_handlers(self) -> None:
        """Initialize support strategy handlers"""
        self._handlers = {
            QueryType.ORDER: OrderSupportStrategy(),
            QueryType.PRODUCT: ProductSupportStrategy(),
            QueryType.GENERAL: GeneralSupportStrategy(),
        }

    @lru_cache(maxsize=1000)
    def _categorize_query(self, message: str) -> QueryType:
        """Categorize queries with caching for performance"""
        message = message.lower()
        
        order_keywords = {"pedido", "compra", "pagamento", "entrega"}
        product_keywords = {"produto", "item", "disponível", "estoque"}
        
        if any(keyword in message for keyword in order_keywords):
            return QueryType.ORDER
        elif any(keyword in message for keyword in product_keywords):
            return QueryType.PRODUCT
        return QueryType.GENERAL

    def _determine_priority(self, message: str, context: Dict) -> Priority:
        """Determine query priority based on message content and context"""
        message = message.lower()
        
        if any(word in message for word in {"urgente", "problema", "erro"}):
            return Priority.URGENT
        if context.get("is_recurring_customer"):
            return Priority.NORMAL
        return Priority.LOW

    def process_message(self, user_id: str, message: str, context: Dict[str, Any]) -> SupportResponse:
        """Process incoming support messages with comprehensive error handling"""
        try:
            if not user_id or not message:
                raise ValueError("Invalid user_id or message")

            query_type = self._categorize_query(message)
            priority = self._determine_priority(message, context)
            
            query = CustomerQuery(
                user_id=user_id,
                message=message,
                timestamp=datetime.utcnow(),
                context=context,
                priority=priority
            )
            
            handler = self._handlers.get(query_type, self._handlers[QueryType.GENERAL])
            response = handler.handle_query(query)
            
            self._cache_response(user_id, response)
            self._log_interaction(query, response)
            
            return response
            
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return self._create_error_response("Invalid input parameters")
        except Exception as e:
            logger.exception("Unexpected error in support processing")
            return self._create_error_response()

    def _create_error_response(self, message: str = "Desculpe, estamos com dificuldades técnicas. Por favor, tente novamente mais tarde.") -> SupportResponse:
        """Create standardized error response"""
        return SupportResponse(
            message=message,
            action_type="error",
            metadata={"error_timestamp": datetime.utcnow().isoformat()}
        )

    def _cache_response(self, user_id: str, response: SupportResponse) -> None:
        """Cache response with size limit management"""
        if len(self._response_cache) > 10000:  # Prevent unlimited growth
            self._response_cache.clear()
        self._response_cache[user_id] = response

    def _log_interaction(self, query: CustomerQuery, response: SupportResponse) -> None:
        """Log interaction details for monitoring and analytics"""
        logger.info({
            "event": "support_interaction",
            "user_id": query.user_id,
            "priority": query.priority.name,
            "query_type": response.action_type,
            "timestamp": response.timestamp.isoformat()
        })
