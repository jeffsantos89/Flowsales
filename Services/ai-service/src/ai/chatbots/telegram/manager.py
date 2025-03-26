import logging
from typing import Optional, Dict, Any
from telegram import Update
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import json
from pathlib import Path
import sys
from functools import wraps

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ChatbotInterface(ABC):
    """Abstract base class for chatbot implementations"""
    @abstractmethod
    async def process_message(self, text: str, user_id: int) -> str:
        pass

class TelegramManager:
    """Manages Telegram bot operations with advanced features and error handling"""
    
    def __init__(
        self,
        token: str,
        chatbot: ChatbotInterface,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize TelegramManager with configuration
        
        Args:
            token (str): Telegram bot token
            chatbot (ChatbotInterface): Chatbot implementation
            max_retries (int): Maximum number of retries for failed operations
            timeout (int): Timeout for operations in seconds
        """
        self.token = token
        self.chatbot = chatbot
        self.max_retries = max_retries
        self.timeout = timeout
        self.application: Optional[Application] = None
        self.active_users: Dict[int, datetime] = {}
        
    def error_handler(func):
        """Decorator for handling errors in async functions"""
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                try:
                    update = args[0]
                    if isinstance(update, Update) and update.effective_chat:
                        await update.effective_chat.send_message(
                            "Sorry, an error occurred. Please try again later."
                        )
                except Exception:
                    logger.error("Could not send error message to user", exc_info=True)
        return wrapper

    async def initialize(self) -> None:
        """Initialize and configure the Telegram bot application"""
        try:
            self.application = Application.builder().token(self.token).build()
            self._register_handlers()
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {str(e)}", exc_info=True)
            raise

    def _register_handlers(self) -> None:
        """Register message and command handlers"""
        if not self.application:
            raise RuntimeError("Application not initialized")
        
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        self.application.add_error_handler(self._error_callback)

    @error_handler
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command"""
        if not update.effective_chat:
            return
        
        user_id = update.effective_chat.id
        self.active_users[user_id] = datetime.now()
        
        welcome_message = (
            "👋 Welcome to the AI Assistant!\n"
            "I'm here to help you. You can start chatting with me right away.\n"
            "Use /help to see available commands."
        )
        await update.effective_chat.send_message(welcome_message)

    @error_handler
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command"""
        if not update.effective_chat:
            return
            
        help_message = (
            "🤖 Available Commands:\n"
            "/start - Start the conversation\n"
            "/help - Show this help message\n"
            "\nJust send me a message and I'll respond!"
        )
        await update.effective_chat.send_message(help_message)

    @error_handler
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming messages"""
        if not update.effective_chat or not update.message or not update.message.text:
            return

        user_id = update.effective_chat.id
        message_text = update.message.text

        # Process message with retry mechanism
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    self.chatbot.process_message(message_text, user_id),
                    timeout=self.timeout
                )
                await update.effective_chat.send_message(response)
                break
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    await update.effective_chat.send_message(
                        "Sorry, the request timed out. Please try again."
                    )
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}", exc_info=True)
                if attempt == self.max_retries - 1:
                    await update.effective_chat.send_message(
                        "Sorry, I couldn't process your message. Please try again later."
                    )

    async def _error_callback(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in the telegram-python-bot library"""
        logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)

    async def start(self) -> None:
        """Start the Telegram bot"""
        if not self.application:
            await self.initialize()
        
        try:
            logger.info("Starting Telegram bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.run_polling()
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {str(e)}", exc_info=True)
            raise

    async def stop(self) -> None:
        """Stop the Telegram bot gracefully"""
        if self.application:
            try:
                logger.info("Stopping Telegram bot...")
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram bot stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Telegram bot: {str(e)}", exc_info=True)