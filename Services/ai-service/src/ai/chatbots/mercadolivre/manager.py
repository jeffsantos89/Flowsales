import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod
import uuid
from dataclasses import dataclass, field
import json
import aiohttp
from contextlib import asynccontextmanager
from enum import Enum
import backoff
from cachetools import TTLCache
from prometheus_client import Counter, Histogram

# Métricas Prometheus
MESSAGE_COUNTER = Counter('ml_messages_total', 'Total messages processed')
PROCESSING_TIME = Histogram('ml_processing_seconds', 'Message processing time')

class MessageType(Enum):
    QUERY = "query"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    ORDER = "order"
    DEFAULT = "default"

@dataclass
class MessageContext:
    user_id: str
    message_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class ChatbotError(Exception):
    pass

class APIError(ChatbotError):
    pass

class MessageHandler(ABC):
    @abstractmethod
    async def process_message(self, message: str, context: MessageContext) -> str:
        pass

    @abstractmethod
    async def can_handle(self, message: str, context: MessageContext) -> bool:
        pass

class MercadoLivreManager:
    def __init__(self, config_path: str = None):
        self.session: Optional[aiohttp.ClientSession] = None
        self.message_handlers: Dict[MessageType, List[MessageHandler]] = {
            type_: [] for type_ in MessageType
        }
        self.config = self._load_config(config_path)
        self.message_queue = asyncio.Queue()
        self.cache = TTLCache(maxsize=1000, ttl=3600)  # Cache with 1 hour TTL
        self._setup_logging()
        
    def _setup_logging(self):
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    @staticmethod
    def _load_config(config_path: Optional[str]) -> Dict[str, Any]:
        logger = logging.getLogger(__name__)
        default_config = {
            "api_base_url": "https://api.mercadolibre.com",
            "max_retries": 3,
            "timeout": 30,
            "batch_size": 100,
            "redis_url": "redis://localhost:6379",
            "max_concurrent_requests": 50,
        }
        
        if not config_path:
            return default_config
            
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                return {**default_config, **user_config}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3
    )
    async def _make_api_request(self, method: str, url: str, **kwargs) -> Dict:
        async with self.get_session() as session:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()

    @asynccontextmanager
    async def get_session(self):
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config['timeout'])
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=aiohttp.TCPConnector(
                    limit=self.config['max_concurrent_requests']
                )
            )
        try:
            yield self.session
        except Exception as e:
            self.logger.error(f"Session error: {e}")
            raise APIError(f"Session error: {e}")

    async def register_handler(self, message_type: MessageType, handler: MessageHandler):
        self.message_handlers[message_type].append(handler)
        self.logger.info(f"Registered handler for message type: {message_type.value}")

    @PROCESSING_TIME.time()
    async def process_message(self, message: str, context: MessageContext) -> str:
        MESSAGE_COUNTER.inc()
        
        try:
            message_type = await self._determine_message_type(message, context)
            handlers = self.message_handlers.get(message_type, [])
            
            if not handlers:
                raise ChatbotError(f"No handlers for message type: {message_type}")
            
            for handler in handlers:
                if await handler.can_handle(message, context):
                    response = await handler.process_message(message, context)
                    await self._store_interaction(context, message, response)
                    return response
                    
            raise ChatbotError("No suitable handler found")
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            raise ChatbotError(f"Message processing error: {e}")

    async def _determine_message_type(self, message: str, context: MessageContext) -> MessageType:
        # Implement message classification logic here
        # Could use ML models, rules, etc.
        return MessageType.DEFAULT

    async def _store_interaction(self, context: MessageContext, message: str, response: str):
        interaction = {
            "user_id": context.user_id,
            "message_id": context.message_id,
            "session_id": context.session_id,
            "timestamp": context.timestamp.isoformat(),
            "message": message,
            "response": response,
            "metadata": context.metadata
        }
        await self.message_queue.put(interaction)

    async def flush_queue(self):
        batch = []
        try:
            while not self.message_queue.empty():
                if len(batch) >= self.config['batch_size']:
                    await self._save_batch(batch)
                    batch = []
                batch.append(await self.message_queue.get())
            
            if batch:
                await self._save_batch(batch)
                
        except Exception as e:
            self.logger.error(f"Error flushing queue: {e}")
            raise ChatbotError(f"Queue flush error: {e}")

    async def _save_batch(self, batch: List[Dict[str, Any]]):
        # Implement persistent storage logic here
        self.logger.info(f"Saving batch of {len(batch)} interactions")

    async def cleanup(self):
        if self.session and not self.session.closed:
            await self.session.close()
        await self.flush_queue()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
