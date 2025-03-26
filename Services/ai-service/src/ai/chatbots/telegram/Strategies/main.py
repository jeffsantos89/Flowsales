"""
main.py
Production-ready Telegram Bot implementation with enhanced error handling, 
logging, and graceful shutdown capabilities.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional
from contextlib import AsyncExitStack, asynccontextmanager
from functools import partial
from ai.chatbots.telegram.telegramBot import TelegramBot
from dotenv import load_dotenv
import os

# Advanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('telegram_bot.log')
    ]
)
logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self):
        self._load_configuration()
        self.bot: Optional[TelegramBot] = None
        self.exit_stack = AsyncExitStack()
        self._shutdown_event = asyncio.Event()
        self._shutdown_timeout = 10  # seconds
        self._is_running = False

    def _load_configuration(self) -> None:
        """Load and validate environment configurations."""
        load_dotenv()
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    @asynccontextmanager
    async def _lifespan(self):
        """Manage the bot's lifecycle."""
        try:
            await self.start()
            yield
        finally:
            await self.stop()

    async def start(self) -> None:
        """Initialize and start the Telegram bot."""
        if self._is_running:
            logger.warning("Bot is already running")
            return

        try:
            self.bot = TelegramBot(self.token)
            await self.bot.start()
            self._is_running = True
            logger.info("Telegram bot started successfully")
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}", exc_info=True)
            raise

    async def stop(self) -> None:
        """Gracefully stop the Telegram bot."""
        if not self._is_running:
            return

        try:
            if self.bot:
                logger.info("Initiating bot shutdown...")
                await asyncio.wait_for(self.bot.stop(), timeout=self._shutdown_timeout)
                self._is_running = False
                logger.info("Telegram bot stopped successfully")
        except asyncio.TimeoutError:
            logger.error("Bot shutdown timed out")
            raise
        except Exception as e:
            logger.error(f"Error during bot shutdown: {str(e)}", exc_info=True)
            raise

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            callback = partial(self.handle_shutdown, sig)
            try:
                asyncio.get_event_loop().add_signal_handler(sig, callback)
                logger.debug(f"Registered signal handler for {sig.name}")
            except NotImplementedError:
                # Windows doesn't support SIGTERM
                logger.warning(f"Signal {sig.name} not supported on this platform")

    def handle_shutdown(self, sig: signal.Signals) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received shutdown signal: {sig.name}")
        self._shutdown_event.set()

    async def run_forever(self) -> None:
        """Run the bot indefinitely until shutdown is requested."""
        self._setup_signal_handlers()

        async with self._lifespan():
            try:
                await self._shutdown_event.wait()
            except Exception as e:
                logger.error(f"Unexpected error during bot operation: {str(e)}", exc_info=True)
                raise

async def main() -> None:
    """Main entry point for the Telegram bot service."""
    try:
        service = TelegramBotService()
        await service.run_forever()
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
