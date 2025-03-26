from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from dataclasses import dataclass
import asyncio
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Enum para tipos de mensagens"""
    WELCOME = "welcome"
    PRODUCT = "product"
    SALES = "sales"
    SUPPORT = "support"
    COMMENT = "comment"
    DEFAULT = "default"
    ERROR = "error"

@dataclass
class MessageContext:
    """Data class to hold message context information"""
    user_id: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]
    intent: Optional[str] = None

    def __post_init__(self):
        """Validate context after initialization"""
        if not self.user_id or not self.message:
            raise ValueError("Invalid message context: user_id and message are required")

class ResponseStrategy(ABC):
    """Abstract base class for all response strategies"""
    
    @abstractmethod
    async def process(self, context: MessageContext) -> Dict[str, Any]:
        """Process the message and return appropriate response"""
        pass

    async def execute(self, context: MessageContext) -> Dict[str, Any]:
        """Template method for executing strategy with logging and error handling"""
        try:
            logger.info(f"[{self.__class__.__name__}] Processing for user: {context.user_id}")
            response = await self.process(context)
            response.update({"timestamp": datetime.now().isoformat()})
            return response
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Error: {str(e)}")
            raise

class WelcomeStrategy(ResponseStrategy):
    """Strategy for handling welcome messages"""
    async def process(self, context: MessageContext) -> Dict[str, Any]:
        return {
            "message_type": MessageType.WELCOME.value,
            "content": "Olá! Bem-vindo(a) ao nosso atendimento no Instagram. Em que posso ajudar?",
            "suggestions": ["Produtos", "Preços", "Suporte", "Ofertas"]
        }

class ProductInquiryStrategy(ResponseStrategy):
    """Strategy for handling product-related inquiries"""
    async def process(self, context: MessageContext) -> Dict[str, Any]:
        products = await self._fetch_products()
        return {
            "message_type": MessageType.PRODUCT.value,
            "content": "Esses são alguns produtos em destaque:",
            "products": products
        }

    async def _fetch_products(self) -> List[Dict[str, Any]]:
        # TODO: Implement actual database query
        await asyncio.sleep(0.2)
        return [{"id": 1, "name": "Produto A", "price": 99.99}]

class SalesStrategy(ResponseStrategy):
    """Strategy for handling sales flow"""
    async def process(self, context: MessageContext) -> Dict[str, Any]:
        return {
            "message_type": MessageType.SALES.value,
            "content": "Ótimo! Temos uma oferta especial para você. Deseja prosseguir com a compra?",
            "actions": ["finalizar_compra", "mais_informacoes", "voltar"]
        }

class SupportStrategy(ResponseStrategy):
    """Strategy for handling support inquiries"""
    async def process(self, context: MessageContext) -> Dict[str, Any]:
        return {
            "message_type": MessageType.SUPPORT.value,
            "content": "Entendi que você precisa de ajuda. Poderia descrever o problema?"
        }

class CommentStrategy(ResponseStrategy):
    """Strategy for handling public comments"""
    async def process(self, context: MessageContext) -> Dict[str, Any]:
        return {
            "message_type": MessageType.COMMENT.value,
            "content": f"Obrigado pelo seu comentário! Respondendo publicamente: '{context.message}'"
        }

class StrategyFactory:
    """Factory class for creating appropriate response strategies"""
    
    _strategies: Dict[str, ResponseStrategy] = {
        MessageType.WELCOME.value: WelcomeStrategy(),
        MessageType.PRODUCT.value: ProductInquiryStrategy(),
        MessageType.SALES.value: SalesStrategy(),
        MessageType.SUPPORT.value: SupportStrategy(),
        MessageType.COMMENT.value: CommentStrategy(),
    }

    @classmethod
    def get_strategy(cls, message_type: str) -> Optional[ResponseStrategy]:
        """Get strategy instance based on message type"""
        return cls._strategies.get(message_type.lower())

    @classmethod
    def register_strategy(cls, message_type: str, strategy: ResponseStrategy) -> None:
        """Register new strategy"""
        cls._strategies[message_type.lower()] = strategy

class MessageProcessor:
    """Main message processor with improved intent detection"""

    def __init__(self):
        self.factory = StrategyFactory()

    async def process_message(self, message: str, user_id: str, 
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process message asynchronously"""
        try:
            metadata = metadata or {}
            intent = self._detect_intent(message, metadata)
            
            context = MessageContext(
                user_id=user_id,
                message=message,
                timestamp=datetime.now(),
                metadata=metadata,
                intent=intent
            )

            strategy = self.factory.get_strategy(intent)
            if not strategy:
                logger.warning(f"No strategy found for intent: {intent}")
                return self._get_default_response()

            return await strategy.execute(context)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return self._get_error_response()

    def _detect_intent(self, message: str, metadata: Dict[str, Any]) -> str:
        """Enhanced intent detection"""
        # Priority 1: Use NLP intent if available
        if intent := metadata.get("intent", "").lower():
            return intent

        # Priority 2: Keyword matching
        message_lower = message.lower()
        keywords = {
            MessageType.SALES.value: ["comprar", "preço", "valor", "pagamento"],
            MessageType.SUPPORT.value: ["ajuda", "suporte", "problema", "dúvida"],
            MessageType.WELCOME.value: ["olá", "oi", "bom dia", "boa tarde", "boa noite"],
            MessageType.PRODUCT.value: ["produto", "catálogo", "mostruário", "disponível"]
        }

        for intent, words in keywords.items():
            if any(word in message_lower for word in words):
                return intent

        # Default to product inquiry if no match
        return MessageType.PRODUCT.value

    def _get_default_response(self) -> Dict[str, Any]:
        return {
            "message_type": MessageType.DEFAULT.value,
            "content": "Desculpe, não entendi. Pode reformular sua pergunta?",
            "timestamp": datetime.now().isoformat()
        }

    def _get_error_response(self) -> Dict[str, Any]:
        return {
            "message_type": MessageType.ERROR.value,
            "content": "Desculpe, ocorreu um erro ao processar sua mensagem.",
            "timestamp": datetime.now().isoformat()
        }
