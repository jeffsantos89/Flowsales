"""
main.py
ShopeeBot implementation with proper error handling, logging, and configuration management.
"""

import logging
import time
from typing import Dict, Optional
from contextlib import contextmanager
from dataclasses import dataclass
import sys
from pathlib import Path
import yaml

from shopee_bot import ShopeeBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('shopee_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BotConfig:
    """Bot configuration parameters"""
    user_id: str
    wait_time: float
    max_retries: int

class ShopeeConversationManager:
    def __init__(self, config_path: Path = Path("config.yaml")):
        self.bot = None
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: Path) -> BotConfig:
        """Load configuration from YAML file"""
        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
                return BotConfig(**config_data)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return BotConfig(
                user_id="default_user",
                wait_time=1.0,
                max_retries=3
            )

    @contextmanager
    def bot_session(self):
        """Context manager for bot lifecycle"""
        try:
            self.bot = ShopeeBot()
            self.bot.start()
            yield self.bot
        except Exception as e:
            self.logger.error(f"Bot session error: {e}")
            raise
        finally:
            if self.bot:
                self.bot.stop()
                self.logger.info(f"Bot final status: {self.bot.get_status()}")

    def process_conversation(self, messages: list) -> list:
        """Process a list of messages with proper error handling"""
        responses = []
        
        with self.bot_session() as bot:
            for message in messages:
                try:
                    response = self._send_message_with_retry(bot, message)
                    responses.append(response)
                    time.sleep(self.config.wait_time)
                except Exception as e:
                    self.logger.error(f"Error processing message '{message}': {e}")
                    responses.append({"error": str(e)})

        return responses

    def _send_message_with_retry(self, bot: ShopeeBot, message: str, 
                               retries: int = None) -> Dict:
        """Send message with retry mechanism"""
        retries = retries or self.config.max_retries
        last_error = None

        for attempt in range(retries):
            try:
                return bot.process_message(self.config.user_id, message)
            except Exception as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(self.config.wait_time)

        raise Exception(f"Failed after {retries} attempts: {last_error}")

def main():
    try:
        # Example conversation
        messages = [
            "Olá, vocês têm tênis Nike?",
            "Qual é o preço médio desse tênis?",
            "Vocês têm disponível no tamanho 42?"
        ]

        manager = ShopeeConversationManager()
        responses = manager.process_conversation(messages)

        for msg, resp in zip(messages, responses):
            logger.info(f"User: {msg}")
            logger.info(f"Bot: {resp.get('response', 'Error: ' + resp.get('error', 'Unknown error'))}")

    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
