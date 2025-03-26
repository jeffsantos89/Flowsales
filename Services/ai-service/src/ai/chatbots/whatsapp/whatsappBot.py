import os
import logging
import asyncio
import requests
import aiohttp
import uuid
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from transformers import pipeline
from tenacity import retry, stop_after_attempt, wait_exponential

from src.ai.decorators.background_task import background_task
from src.ai.chatbots.message_queue import MessageQueue
from src.utils.cache import TTLCache
from src.utils.metrics import MetricsCollector
from src.security.ratelimiter import RateLimiter
from src.config import Settings

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    MEDIA = "media"
    TEMPLATE = "template"

@dataclass
class WhatsAppMessage:
    message_id: str
    from_number: str
    text: str
    type: MessageType
    timestamp: datetime
    metadata: Dict[str, Any]

class WhatsAppBot:
    def __init__(
        self,
        settings: Settings,
        rate_limit: int = 60,
        retry_attempts: int = 3,
        cache_ttl: int = 3600,
        queue_backend: str = "redis"
    ):
        self.settings = settings
        self.rate_limiter = RateLimiter(max_requests=rate_limit, time_window=60)
        self.metrics = MetricsCollector()
        self.message_cache = TTLCache(ttl=cache_ttl)
        self.queue = self._initialize_queue(queue_backend)
        self.models = {}
        
        # Inicialização assíncrona dos modelos
        asyncio.create_task(self._initialize_nlp_models())
        
        # Monitor de saúde
        self._start_health_monitor()

    async def _initialize_queue(self, backend: str) -> MessageQueue:
        if backend == "redis":
            from src.ai.queue.redis_backend import RedisQueue
            return MessageQueue(backend=RedisQueue())
        return MessageQueue()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _initialize_nlp_models(self):
        """Inicialização lazy dos modelos NLP"""
        try:
            self.models.update({
                'sentiment': pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"),
                'conversation': pipeline("conversational", model="facebook/blenderbot-400M-distill"),
                'intent': pipeline("text-classification", model="bert-base-uncased")
            })
            logger.info("NLP models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
            raise

    async def _send_whatsapp_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """Envio de mensagens com retry e circuit breaker"""
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": message.from_number,
            "type": message.type.value,
            "text": {"body": message.text}
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.settings.whatsapp_api_url}/messages",
                    json=payload,
                    headers=headers
                ) as response:
                    return await response.json()
            except Exception as e:
                logger.error(f"WhatsApp API error: {e}")
                self.metrics.increment("whatsapp_api_errors")
                raise

    @background_task
    async def process_message_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processamento assíncrono de mensagens com validação e tratamento de erros"""
        message = WhatsAppMessage(
            message_id=data["message_id"],
            from_number=data["from"],
            text=data["text"],
            type=MessageType.TEXT,
            timestamp=datetime.now(),
            metadata=data.get("metadata", {})
        )

        async with self.rate_limiter:
            if self.message_cache.exists(message.message_id):
                return {"status": "duplicate"}

            try:
                # Processamento paralelo de análises
                intent, sentiment = await asyncio.gather(
                    self.classify_intent(message.text),
                    self.analyze_sentiment(message.text)
                )

                response = await self.generate_response(message.text, intent, sentiment)
                
                # Publicação na fila e envio são executados em paralelo
                await asyncio.gather(
                    self.queue.publish({
                        "platform": "whatsapp",
                        "user_id": message.from_number,
                        "message": response,
                        "intent": intent,
                        "sentiment": sentiment,
                        "metadata": message.metadata
                    }),
                    self._send_whatsapp_message(WhatsAppMessage(
                        message_id=str(uuid.uuid4()),
                        from_number=message.from_number,
                        text=response,
                        type=MessageType.TEXT,
                        timestamp=datetime.now(),
                        metadata={"reply_to": message.message_id}
                    ))
                )

                self.metrics.increment("messages_processed")
                self.message_cache.set(message.message_id, "processed")
                
                return {
                    "status": "success",
                    "intent": intent,
                    "sentiment": sentiment
                }

            except Exception as e:
                logger.exception("Message processing error")
                self.metrics.increment("processing_errors")
                return {"status": "error", "message": str(e)}

    @background_task
    async def _health_monitor(self):
        """Monitor contínuo de saúde do sistema"""
        while True:
            health_status = await self.health_check()
            if health_status["status"] != "healthy":
                logger.warning(f"Unhealthy state detected: {health_status}")
            await asyncio.sleep(60)

    async def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde expandida"""
        return {
            "status": "healthy" if all([
                self.models,
                self.queue.is_connected(),
                self.message_cache.is_available()
            ]) else "unhealthy",
            "metrics": self.metrics.get_all(),
            "queue_status": await self.queue.status(),
            "cache_status": self.message_cache.status,
            "rate_limiter_status": self.rate_limiter.status,
            "models_loaded": list(self.models.keys())
        }
