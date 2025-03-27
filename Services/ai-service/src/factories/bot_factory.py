from abc import ABC, abstractmethod
from typing import Dict, Type, Optional
from logging import getLogger, Logger
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

class BotType(Enum):
    """Enum defining supported bot types"""
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    MESSENGER = "messenger"
    DISCORD = "discord"

@dataclass
class BotConfig:
    """Data class for bot configuration"""
    api_key: str
    platform: BotType
    max_retries: int = 3
    timeout: int = 30
    debug_mode: bool = False

class Bot(ABC):
    """Abstract base class for all bot implementations"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize bot connection"""
        pass

    @abstractmethod
    async def send_message(self, recipient_id: str, message: str) -> bool:
        """Send message through the bot"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean disconnect from platform"""
        pass

class BotFactory:
    """Factory class for creating and managing bot instances"""
    
    def __init__(self):
        self._bots: Dict[BotType, Type[Bot]] = {}
        self._instances: Dict[str, Bot] = {}
        self._logger: Logger = getLogger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=4)
        
    def register_bot(self, bot_type: BotType, bot_class: Type[Bot]) -> None:
        """Register a new bot type implementation"""
        self._bots[bot_type] = bot_class
        self._logger.info(f"Registered bot type: {bot_type.value}")

    async def create_bot(self, config: BotConfig) -> Optional[Bot]:
        """Create a new bot instance based on configuration"""
        try:
            if config.platform not in self._bots:
                self._logger.error(f"Unsupported bot type: {config.platform.value}")
                return None

            bot_class = self._bots[config.platform]
            instance = bot_class()
            
            # Initialize bot with retry mechanism
            for attempt in range(config.max_retries):
                try:
                    success = await instance.initialize()
                    if success:
                        self._instances[config.api_key] = instance
                        self._logger.info(f"Successfully created {config.platform.value} bot instance")
                        return instance
                except Exception as e:
                    self._logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    await asyncio.sleep(1)
            
            self._logger.error(f"Failed to initialize bot after {config.max_retries} attempts")
            return None

        except Exception as e:
            self._logger.error(f"Error creating bot: {str(e)}")
            return None

    async def get_bot(self, api_key: str) -> Optional[Bot]:
        """Retrieve an existing bot instance"""
        return self._instances.get(api_key)

    async def shutdown(self) -> None:
        """Gracefully shutdown all bot instances"""
        try:
            shutdown_tasks = [
                instance.disconnect() 
                for instance in self._instances.values()
            ]
            await asyncio.gather(*shutdown_tasks)
            self._executor.shutdown(wait=True)
            self._logger.info("All bot instances shut down successfully")
        except Exception as e:
            self._logger.error(f"Error during shutdown: {str(e)}")

# Singleton instance
_bot_factory: Optional[BotFactory] = None

def get_bot_factory() -> BotFactory:
    """Get or create the singleton BotFactory instance"""
    global _bot_factory
    if _bot_factory is None:
        _bot_factory = BotFactory()
    return _bot_factory