from typing import Optional, Dict, Any, List, TYPE_CHECKING
import logging
from dataclasses import dataclass
from datetime import datetime
import asyncio
from telegram import Update, Message, Document, PhotoSize
from telegram.ext import ContextTypes
import aiohttp
import json
from enum import Enum
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from nlp.huggingface_processor import HuggingFaceProcessor

# Configure logging with a more detailed format
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    PHOTO = "photo"
    DOCUMENT = "document"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class QueryResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    message_type: MessageType = MessageType.UNKNOWN

class QueryProcessor(ABC):
    @abstractmethod
    async def process(self, query_data: Dict[str, Any], **kwargs) -> QueryResult:
        pass

class TextQueryProcessor(QueryProcessor):
    def __init__(self, session: aiohttp.ClientSession, api_key: str, endpoint: str, timeout: int):
        self.session = session
        self.api_key = api_key
        self.endpoint = endpoint
        self.timeout = timeout

    async def process(self, query_data: Dict[str, Any], **kwargs) -> QueryResult:
        try:
            async with self.session.post(
                self.endpoint,
                json=query_data,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return QueryResult(success=True, data=data, message_type=MessageType.TEXT)
                return QueryResult(
                    success=False,
                    error=f"API request failed with status {response.status}",
                    message_type=MessageType.TEXT
                )
        except Exception as e:
            logger.error(f"Text processing error: {str(e)}", exc_info=True)
            return QueryResult(success=False, error=str(e), message_type=MessageType.TEXT)

class TelegramQueryHandler:
    def __init__(self, 
                 api_key: str, 
                 endpoint: str,
                 max_retries: int = 3, 
                 timeout: int = 30,
                 nlp_processor: Optional['HuggingFaceProcessor'] = None):
        self.api_key = api_key
        self.endpoint = endpoint
        self.max_retries = max_retries
        self.timeout = timeout
        self.nlp_processor = nlp_processor
        self._session: Optional[aiohttp.ClientSession] = None
        self._processors: Dict[MessageType, QueryProcessor] = {}

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        self._setup_processors()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    def _setup_processors(self):
        self._processors[MessageType.TEXT] = TextQueryProcessor(
            self._session,
            self.api_key,
            self.endpoint,
            self.timeout
        )

    async def process_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> QueryResult:
        """Process incoming Telegram queries with retry and error handling"""
        try:
            if not update.message:
                return QueryResult(success=False, error="No message found in update")

            return await self._handle_message_with_retry(update.message, context)

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return QueryResult(success=False, error=f"Internal error: {str(e)}")

    async def _handle_message_with_retry(
        self, 
        message: Message, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> QueryResult:
        """Handle message processing with retry mechanism"""
        query_data = self._extract_message_data(message)
        
        if self.nlp_processor:
            nlp_result = await self._process_nlp(message.text) if message.text else None
            if nlp_result:
                query_data.update(nlp_result)

        for attempt in range(self.max_retries):
            try:
                result = await self._process_message(message, query_data)
                if result.success:
                    return result
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
                return result

            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    return QueryResult(success=False, error="Request timeout")
                await asyncio.sleep(2 ** attempt)

    def _extract_message_data(self, message: Message) -> Dict[str, Any]:
        """Extract common message metadata"""
        return {
            "message_id": message.message_id,
            "chat_id": message.chat_id,
            "user_id": message.from_user.id if message.from_user else None,
            "text": message.text,
            "timestamp": message.date.isoformat(),
        }

    async def _process_nlp(self, text: str) -> Dict[str, Any]:
        """Process text through NLP pipeline"""
        try:
            cleaned = text.strip().lower()
            nlp_result = await self.nlp_processor.analyze(cleaned)
            logger.debug(f"NLP result: {nlp_result}")
            return {
                "intent": nlp_result.get("intent", "unknown"),
                "entities": nlp_result.get("entities", [])
            }
        except Exception as e:
            logger.exception("Error in NLP processing")
            return {"intent": "error", "entities": [], "error": str(e)}

    async def _process_message(self, message: Message, query_data: Dict[str, Any]) -> QueryResult:
        """Process message based on its type"""
        message_type = self._determine_message_type(message)
        processor = self._processors.get(message_type)
        
        if not processor:
            return QueryResult(
                success=False,
                error=f"Unsupported message type: {message_type}",
                message_type=message_type
            )
            
        return await processor.process(query_data)

    @staticmethod
    def _determine_message_type(message: Message) -> MessageType:
        """Determine the type of message"""
        if message.text:
            return MessageType.TEXT
        elif message.photo:
            return MessageType.PHOTO
        elif message.document:
            return MessageType.DOCUMENT
        return MessageType.UNKNOWN

    @staticmethod
    def format_response(query_result: QueryResult) -> str:
        """Format query result for response"""
        if query_result.success:
            return json.dumps(query_result.data, indent=2)
        return f"Error: {query_result.error}"
