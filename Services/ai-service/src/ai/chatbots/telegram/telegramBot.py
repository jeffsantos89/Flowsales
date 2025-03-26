import os
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto
import logging
from functools import wraps

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
    ContextTypes
)

from ai.nlp.huggingface_processor import HuggingFaceProcessor
from ai.database.sales import SalesDatabase
from security.ratelimiter import RateLimiter
from utils.cache import TTLCache
from utils.logger import logger
from ai.chatbots.telegram.query import TelegramQueryPipeline
from ai.chatbots.telegram.strategies import (
    BaseStrategy,
    ProductSearchStrategy,
    PriceComparisonStrategy
)

class ConversationState(Enum):
    INITIAL = auto()
    PRODUCT = auto() 
    PRICE = auto()
    IDLE = auto()

@dataclass
class Conversation:
    state: ConversationState
    messages: list
    context: dict
    last_interaction: float

class TelegramBotConfig:
    def __init__(self, **kwargs):
        self.token = kwargs.get('token')
        self.max_conversations = kwargs.get('max_conversations', 1000)
        self.message_timeout = kwargs.get('message_timeout', 300)
        self.cache_ttl = kwargs.get('cache_ttl', 3600)
        self.rate_limit = kwargs.get('rate_limit', {'requests': 30, 'window': 60})

def async_error_handler(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            # Notify monitoring system
            raise
    return wrapper

class TelegramBot:
    """
    Advanced Telegram Bot with NLP capabilities and sophisticated conversation management
    """
    def __init__(self, config: TelegramBotConfig):
        self.config = config
        self.application: Optional[Application] = None
        self._setup_dependencies()
        self._setup_strategies()
        self.conversations: Dict[str, Conversation] = {}
        self._cleanup_task = None

    def _setup_dependencies(self):
        """Initialize core dependencies"""
        self.nlp = HuggingFaceProcessor()
        self.sales_db = SalesDatabase()
        self.rate_limiter = RateLimiter(**self.config.rate_limit)
        self.cache = TTLCache(ttl=self.config.cache_ttl)
        self.query_pipeline = TelegramQueryPipeline(self.nlp)

    def _setup_strategies(self):
        """Initialize conversation strategies"""
        self.strategies = {
            "product_search": ProductSearchStrategy(self.sales_db),
            "price_comparison": PriceComparisonStrategy(self.sales_db),
        }

    async def _cleanup_conversations(self):
        """Periodic cleanup of stale conversations"""
        while True:
            try:
                current_time = asyncio.get_event_loop().time()
                stale_users = [
                    user_id for user_id, conv in self.conversations.items()
                    if current_time - conv.last_interaction > self.config.message_timeout
                ]
                for user_id in stale_users:
                    del self.conversations[user_id]
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")

    @async_error_handler
    async def start(self):
        """Start the Telegram bot application"""
        self.application = (
            ApplicationBuilder()
            .token(self.config.token)
            .concurrent_updates(True)
            .build()
        )

        self._register_handlers()
        
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        self._cleanup_task = asyncio.create_task(self._cleanup_conversations())
        
        logger.info("Telegram Bot started successfully")

    @async_error_handler
    async def stop(self):
        """Gracefully stop the bot"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            
        logger.info("Telegram Bot stopped successfully")

    def _register_handlers(self):
        """Register message handlers"""
        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(CommandHandler("help", self._handle_help))
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self._handle_message
        ))
        self.application.add_error_handler(self._handle_error)

    @async_error_handler
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = str(update.effective_user.id)
        self._init_conversation(user_id)
        await update.message.reply_text(
            "👋 Olá! Sou um bot especializado em buscas e comparações de produtos.\n"
            "Como posso ajudar você hoje?"
        )

    @async_error_handler
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process incoming messages"""
        user_id = str(update.effective_user.id)
        text = update.message.text

        if self.rate_limiter.is_blocked(user_id):
            await update.message.reply_text(
                "⚠️ Taxa limite excedida. Por favor, aguarde um momento."
            )
            return

        if cached_response := self.cache.get(user_id, text):
            await update.message.reply_text(cached_response["response"])
            return

        conversation = self._get_or_create_conversation(user_id)
        query_info = self.query_pipeline.process(text)
        
        strategy = self._get_strategy(query_info.get("intent", "unknown"))
        result = await strategy.execute(user_id, text, query_info, conversation)

        self._update_conversation(user_id, text, query_info)
        self.cache.set(user_id, text, result)

        await update.message.reply_text(result.get("response", "Desculpe, não entendi."))

    def _get_or_create_conversation(self, user_id: str) -> Conversation:
        """Get existing conversation or create new one"""
        if user_id not in self.conversations:
            self._init_conversation(user_id)
        return self.conversations[user_id]

    def _init_conversation(self, user_id: str):
        """Initialize new conversation"""
        self.conversations[user_id] = Conversation(
            state=ConversationState.INITIAL,
            messages=[],
            context={},
            last_interaction=asyncio.get_event_loop().time()
        )

    def _update_conversation(self, user_id: str, text: str, query_info: dict):
        """Update conversation state and history"""
        conversation = self.conversations[user_id]
        conversation.messages.append({"text": text, "intent": query_info.get("intent")})
        conversation.last_interaction = asyncio.get_event_loop().time()

    def _get_strategy(self, intent: str) -> BaseStrategy:
        """Get appropriate strategy based on intent"""
        return self.strategies.get(
            self._map_intent_to_strategy(intent),
            self.strategies["product_search"]
        )

    @staticmethod
    def _map_intent_to_strategy(intent: str) -> str:
        """Map NLP intent to strategy"""
        intent_mapping = {
            "product_info": "product_search",
            "price_comparison": "price_comparison"
        }
        return intent_mapping.get(intent, "product_search")

    async def _handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler"""
        logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)
        if update:
            await update.message.reply_text(
                "Desculpe, ocorreu um erro ao processar sua mensagem. "
                "Por favor, tente novamente mais tarde."
            )

    def get_status(self) -> Dict[str, Any]:
        """Get bot status information"""
        return {
            "active_sessions": len(self.conversations),
            "cache_size": len(self.cache),
            "rate_limited_users": self.rate_limiter.get_blocked_users()
        }
