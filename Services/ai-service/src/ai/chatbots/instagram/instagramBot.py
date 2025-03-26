from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio

from nlp_processor import NLPProcessor
from product_database import ProductDatabase
from message_queue import MessageQueue
from ai.nlp.huggingface_processor import HuggingFaceProcessor
from ai.queue.redis_backend import RedisQueue
from ai.database.sales import SalesDatabase
from ai.ticketing import TicketingSystem
from security.ratelimiter import RateLimiter
from utils.cache import TTLCache
from utils.logger import logger
from ai.decorators.retry import retry
from ai.decorators.background_task import background_task
from .strategies.strategies import MessageProcessor

class MessageIntent(Enum):
    PRODUCT_INFO = "product_info"
    SUPPORT = "support"
    GENERAL = "general"
    SALES = "sales"
    COMPLAINT = "complaint"

@dataclass
class ConversationEntry:
    query: str
    intent: MessageIntent
    response: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

class InstagramChatBot:
    """
    Chatbot avançado para Instagram com suporte a processamento assíncrono,
    rate limiting, cache e recursos de resiliência.
    """

    def __init__(
        self,
        nlp_processor: Optional[NLPProcessor] = None,
        product_db: Optional[ProductDatabase] = None,
        message_queue: Optional[MessageQueue] = None,
        message_processor: Optional[MessageProcessor] = None,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[TTLCache] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.conversation_history: Dict[str, List[ConversationEntry]] = {}
        self.nlp = nlp_processor or HuggingFaceProcessor()
        self.product_db = product_db or ProductDatabase()
        self.queue = message_queue or RedisQueue()
        self.message_processor = message_processor or MessageProcessor()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.cache = cache or TTLCache()
        self.ticketing_system = TicketingSystem()

    @retry(max_attempts=3, delay=1)
    async def handle_customer_query(
        self, 
        query: str, 
        customer_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa queries do cliente de forma assíncrona com retry automático
        e controle de rate limiting.
        """
        try:
            user_id = customer_id or "anonymous"
            await self.rate_limiter.check_limit(user_id)

            # Verifica cache primeiro
            cache_key = f"{user_id}:{query}"
            if cached_response := await self.cache.get(cache_key):
                return cached_response

            # Inicializa histórico se necessário
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            # Análise de intenção com contexto
            intent = await self.analyze_intent(query, context)
            metadata = {
                "intent": intent,
                "channel": "instagram",
                "context": context or {},
                "timestamp": datetime.utcnow()
            }

            # Processamento assíncrono da mensagem
            response_data = await self.process_message(
                query, user_id, metadata
            )

            # Atualiza histórico
            entry = ConversationEntry(
                query=query,
                intent=intent,
                response=response_data["content"],
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            self.conversation_history[user_id].append(entry)

            # Publica eventos relevantes
            await self.publish_events(user_id, query, response_data, metadata)

            # Cache da resposta
            await self.cache.set(cache_key, response_data, ttl=300)

            return response_data

        except Exception as e:
            await self.handle_error(e, user_id, query)
            return {
                "content": "Desculpe, ocorreu um erro. Por favor, tente novamente.",
                "error": str(e)
            }

    @background_task
    async def analyze_intent(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> MessageIntent:
        """Análise avançada de intenção com contexto"""
        intent_str = await self.nlp.classify_intent(query, context)
        return MessageIntent(intent_str)

    async def process_message(
        self, 
        message: str, 
        user_id: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Processamento assíncrono de mensagens"""
        return await self.message_processor.process_message(
            message=message,
            user_id=user_id,
            metadata=metadata
        )

    async def publish_events(
        self, 
        user_id: str, 
        query: str, 
        response_data: Dict[str, Any], 
        metadata: Dict[str, Any]
    ) -> None:
        """Publica eventos para processamento assíncrono"""
        event_data = {
            'type': 'instagram_interaction',
            'channel': 'instagram',
            'user_id': user_id,
            'message': query,
            'response': response_data,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.queue.publish(event_data)

    async def handle_error(
        self, 
        error: Exception, 
        user_id: str, 
        query: str
    ) -> None:
        """Tratamento centralizado de erros"""
        self.logger.error(
            f"Error processing message for user {user_id}: {str(error)}",
            exc_info=True
        )
        await self.ticketing_system.create_ticket({
            'user_id': user_id,
            'error': str(error),
            'query': query,
            'timestamp': datetime.utcnow()
        })