import logging
from typing import Dict, List, Any, Type
from datetime import datetime
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Data class to represent a chat message"""
    content: str
    timestamp: datetime
    sender: str
    metadata: Dict[str, Any]

class AmazonChatbotError(Exception):
    """Custom exception for Amazon chatbot operations"""
    pass

class AmazonChatStrategy:
    """Base class for different chatbot strategies"""
    async def process(self, message: ChatMessage) -> ChatMessage:
        raise NotImplementedError("Strategy must implement process method")

class ProductSearchStrategy(AmazonChatStrategy):
    async def process(self, message: ChatMessage) -> ChatMessage:
        # Implement product search logic here
        pass

class PriceComparisonStrategy(AmazonChatStrategy):
    async def process(self, message: ChatMessage) -> ChatMessage:
        # Implement price comparison logic here
        pass

class AmazonChatbotManager:
    """Main manager class for handling Amazon chatbot operations"""
    def __init__(self, config_path: str = "config/amazon_config.json"):
        self._executor = ThreadPoolExecutor(max_workers=os.cpu_count())
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._strategies: Dict[str, AmazonChatStrategy] = {}
        self._config = self._load_config(config_path)
        self._initialize_strategies()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}. Using default configuration.")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            raise AmazonChatbotError("Invalid configuration file")

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "strategies": ["product_search", "price_comparison"],
            "timeout": 30,
            "batch_size": 100
        }

    def _initialize_strategies(self) -> None:
        """Initialize chatbot strategies based on configuration"""
        mapping: Dict[str, Type[AmazonChatStrategy]] = {
            "product_search": ProductSearchStrategy,
            "price_comparison": PriceComparisonStrategy,
        }
        for name in self._config["strategies"]:
            strategy_class = mapping.get(name)
            if strategy_class:
                self._strategies[name] = strategy_class()

    async def process_message(self, message: str, strategy: str = "product_search") -> str:
        """Process a single message using the specified strategy"""
        try:
            chat_message = ChatMessage(
                content=message,
                timestamp=datetime.now(),
                sender="user",
                metadata={}
            )
            if strategy not in self._strategies:
                raise AmazonChatbotError(f"Strategy '{strategy}' not found")

            result = await self._strategies[strategy].process(chat_message)
            await self._message_queue.put(result)
            return result.content if hasattr(result, "content") else str(result)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise AmazonChatbotError(f"Failed to process message: {str(e)}")

    async def batch_process_messages(self, messages: List[str]) -> List[str]:
        """Process multiple messages in batch"""
        tasks = [self.process_message(msg) for msg in messages]
        return await asyncio.gather(*tasks)

    async def _message_processor(self) -> None:
        """Background task to process messages from queue"""
        while True:
            message = await self._message_queue.get()
            try:
                logger.debug(f"Processing message: {message}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
            finally:
                self._message_queue.task_done()

    async def start(self) -> None:
        """Start the chatbot manager"""
        logger.info("Starting Amazon Chatbot Manager")
        await self._message_processor()

    def shutdown(self) -> None:
        """Cleanup and shutdown the manager"""
        logger.info("Shutting down Amazon Chatbot Manager")
        self._executor.shutdown(wait=True)

    def get_statistics(self) -> Dict[str, Any]:
        """Get operational statistics"""
        return {
            "queue_size": self._message_queue.qsize(),
            "active_strategies": list(self._strategies.keys())
        }
