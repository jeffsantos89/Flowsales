from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Protocol
from datetime import datetime
import logging
import json
import os
import asyncio
from logging.handlers import RotatingFileHandler
from enum import Enum
from contextlib import asynccontextmanager
import aiohttp
import backoff
from cachetools import TTLCache
from prometheus_client import Counter, Histogram

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    VOICE = "voice"

class MessageStatus(Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass(frozen=True)
class WhatsAppMessage:
    message_id: str
    from_number: str
    to_number: str
    content: str
    timestamp: datetime
    media_url: Optional[str] = None
    message_type: MessageType = MessageType.TEXT
    status: MessageStatus = MessageStatus.RECEIVED
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "from_number": self.from_number,
            "to_number": self.to_number,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "media_url": self.media_url,
            "message_type": self.message_type.value,
            "status": self.status.value,
            "metadata": self.metadata or {}
        }

class HandlerResult(Protocol):
    success: bool
    error_message: Optional[str]
    processed_data: Optional[Dict[str, Any]]

class WhatsAppHandler(ABC):
    @abstractmethod
    async def handle_message(self, message: WhatsAppMessage) -> HandlerResult:
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        pass

class WhatsAppManager:
    def __init__(self, api_key: str, webhook_url: str):
        self._api_key = api_key
        self._webhook_url = webhook_url
        self._handlers: Dict[MessageType, List[WhatsAppHandler]] = {}
        self._message_cache = TTLCache(maxsize=1000, ttl=3600)  # Cache messages for 1 hour
        self._setup_metrics()
        self._setup_logging()
        self._load_config()
        self._session: Optional[aiohttp.ClientSession] = None

    def _setup_metrics(self):
        self.message_counter = Counter(
            'whatsapp_messages_total',
            'Total WhatsApp messages processed',
            ['message_type', 'status']
        )
        self.processing_time = Histogram(
            'whatsapp_processing_time_seconds',
            'Time spent processing messages'
        )

    def _setup_logging(self):
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
            
        self.logger = logging.getLogger("WhatsAppManager")
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler = RotatingFileHandler(
            f"{log_dir}/whatsapp_manager.log",
            maxBytes=10485760,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _load_config(self):
        try:
            with open("config/whatsapp_config.json", "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.logger.warning("Config file not found, using defaults")
            self.config = {
                "retry_attempts": 3,
                "timeout": 30,
                "max_concurrent_connections": 100,
                "rate_limit": 100,  # messages per second
                "batch_size": 50
            }

    @asynccontextmanager
    async def get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=aiohttp.ClientTimeout(total=self.config["timeout"])
            )
        try:
            yield self._session
        except Exception as e:
            self.logger.error(f"Session error: {str(e)}")
            await self._session.close()
            self._session = None
            raise

    async def register_handler(self, message_type: MessageType, handler: WhatsAppHandler):
        if not isinstance(handler, WhatsAppHandler):
            raise ValueError("Handler must implement WhatsAppHandler interface")
        
        if message_type not in self._handlers:
            self._handlers[message_type] = []
        
        self._handlers[message_type].append(handler)
        self.logger.info(f"Registered handler for message type: {message_type.value}")

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3
    )
    async def process_message(self, raw_message: Dict[str, Any]) -> None:
        message_id = raw_message.get("id")
        
        # Deduplication check
        if message_id in self._message_cache:
            self.logger.info(f"Duplicate message detected: {message_id}")
            return

        try:
            with self.processing_time.time():
                message = self._parse_message(raw_message)
                self._message_cache[message_id] = message
                
                handlers = self._handlers.get(message.message_type, [])
                if not handlers:
                    self.logger.warning(f"No handlers found for message type: {message.message_type}")
                    return

                tasks = [self._execute_with_retry(handler.handle_message, message) 
                        for handler in handlers]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                await self._process_results(message, results)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
            self.message_counter.labels(
                message_type=message.message_type.value,
                status="failed"
            ).inc()
            raise

    async def _process_results(self, message: WhatsAppMessage, results: List[HandlerResult]):
        success = all(
            isinstance(result, HandlerResult) and result.success 
            for result in results
        )
        
        status = MessageStatus.COMPLETED if success else MessageStatus.FAILED
        self.message_counter.labels(
            message_type=message.message_type.value,
            status=status.value
        ).inc()

    async def cleanup(self):
        """Cleanup resources when shutting down"""
        if self._session and not self._session.closed:
            await self._session.close()
        
        for handlers in self._handlers.values():
            for handler in handlers:
                await handler.cleanup()

    def _parse_message(self, raw_message: Dict[str, Any]) -> WhatsAppMessage:
        try:
            return WhatsAppMessage(
                message_id=raw_message["id"],
                from_number=raw_message["from"],
                to_number=raw_message["to"],
                content=raw_message.get("content", ""),
                timestamp=datetime.fromisoformat(raw_message["timestamp"]),
                media_url=raw_message.get("media_url"),
                message_type=MessageType(raw_message.get("type", "text")),
                metadata=raw_message.get("metadata", {})
            )
        except (KeyError, ValueError) as e:
            self.logger.error(f"Error parsing message: {str(e)}")
            raise ValueError(f"Invalid message format: {str(e)}")