from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from enum import Enum
import json
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import traceback

class FacebookQueryPipeline:
    async def process_message(self, text: str) -> Dict[str, Any]:
        # Implement your NLP logic here
        return {
            'intent': 'default',
            'confidence': 1.0,
            'entities': []
        }

# Advanced logging configuration
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'facebook_bot.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        }
    }
})

logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    ATTACHMENT = "attachment"
    QUICK_REPLY = "quick_reply"
    POSTBACK = "postback"
    REACTION = "reaction"

@dataclass
class FacebookMessage:
    """Enhanced data class for Facebook message information"""
    message_id: str
    sender_id: str
    recipient_id: str
    timestamp: datetime
    message_type: MessageType
    text: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    quick_reply: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type.value,
            'text': self.text,
            'attachments': self.attachments,
            'quick_reply': self.quick_reply,
            'metadata': self.metadata
        }

class MessageProcessingError(Exception):
    """Custom exception for message processing errors"""
    pass

class QueryInterface(ABC):
    """Enhanced abstract base class for query operations"""
    @abstractmethod
    async def process_message(self, message: FacebookMessage) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def validate_payload(self, payload: Dict[str, Any]) -> bool:
        pass

class FacebookMessageQuery(QueryInterface):
    """Enhanced class to handle Facebook message queries"""
    
    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.supported_message_types = set(MessageType)
        self.max_retries = max_retries
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._session = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Lazy initialization of aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session

    @lru_cache(maxsize=1000)
    async def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate incoming Facebook payload with caching"""
        try:
            if not isinstance(payload, dict):
                raise ValueError("Invalid payload type")
            
            required_fields = {'messaging', 'sender', 'recipient'}
            if not all(field in payload for field in required_fields):
                raise ValueError("Missing required fields in payload")
                
            return True
        except Exception as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            return False

    async def extract_message_data(self, payload: Dict[str, Any]) -> FacebookMessage:
        """Extract relevant data from Facebook payload with enhanced error handling"""
        try:
            messaging = payload['messaging'][0]
            message = messaging.get('message', {})
            
            message_type = MessageType.TEXT
            if message.get('attachments'):
                message_type = MessageType.ATTACHMENT
            elif message.get('quick_reply'):
                message_type = MessageType.QUICK_REPLY

            return FacebookMessage(
                message_id=message.get('mid'),
                sender_id=messaging['sender']['id'],
                recipient_id=messaging['recipient']['id'],
                timestamp=datetime.fromtimestamp(messaging.get('timestamp', 0) / 1000),
                message_type=message_type,
                text=message.get('text'),
                attachments=message.get('attachments', []),
                quick_reply=message.get('quick_reply'),
                metadata={'page_id': payload.get('page_id')},
                raw_payload=payload
            )
        except Exception as e:
            logger.error(f"Error extracting message data: {traceback.format_exc()}")
            raise MessageProcessingError(f"Failed to extract message data: {str(e)}")

    async def process_message(self, message: FacebookMessage) -> Dict[str, Any]:
        """Process Facebook message asynchronously"""
        try:
            response = {
                'recipient': {'id': message.sender_id},
                'messaging_type': 'RESPONSE',
                'message': {}
            }

            processor_map = {
                MessageType.TEXT: self._process_text_message,
                MessageType.ATTACHMENT: self._process_attachments,
                MessageType.QUICK_REPLY: self._process_quick_reply
            }

            processor = processor_map.get(message.message_type)
            if processor:
                result = await processor(message)
                response['message'].update(result)
            
            logger.info(f"Processed message for sender {message.sender_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {traceback.format_exc()}")
            raise MessageProcessingError(f"Failed to process message: {str(e)}")

    async def _process_text_message(self, message: FacebookMessage) -> Dict[str, Any]:
        """Process text messages with NLP integration"""
        pipeline = FacebookQueryPipeline()
        nlp_result = await pipeline.process_message(message.text)
        return {
            'text': f"Processed message. Intent: {nlp_result['intent']}",
            'metadata': nlp_result
        }

    async def _process_attachments(self, message: FacebookMessage) -> Dict[str, Any]:
        """Process message attachments asynchronously"""
        tasks = [self._process_single_attachment(att) for att in message.attachments]
        results = await asyncio.gather(*tasks)
        return {'attachment_results': results}

    async def _process_single_attachment(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single attachment"""
        # Implement attachment processing logic
        return {'type': attachment.get('type'), 'status': 'processed'}

    async def _process_quick_reply(self, message: FacebookMessage) -> Dict[str, Any]:
        """Process quick reply messages"""
        return {
            'text': f"Quick reply processed: {message.quick_reply.get('payload')}",
            'metadata': {'quick_reply_type': message.quick_reply.get('type')}
        }

    async def close(self):
        """Cleanup resources"""
        if self._session:
            await self._session.close()
        self.executor.shutdown()

class QueryFactory:
    """Enhanced factory class for creating query instances"""
    
    _instances: Dict[str, QueryInterface] = {}
    
    @classmethod
    def get_query(cls, query_type: str = 'facebook') -> QueryInterface:
        """Get or create query instance (singleton pattern)"""
        if query_type.lower() not in cls._instances:
            if query_type.lower() == 'facebook':
                cls._instances[query_type] = FacebookMessageQuery()
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
        return cls._instances[query_type]
