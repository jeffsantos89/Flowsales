# src/routes/telegram_handler.py

import logging
from typing import AsyncGenerator, Dict, Any
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from contextlib import asynccontextmanager

from telegramBot import TelegramBot
from ai.queue.redis_backend import RedisQueue
from ai.nlp.huggingface_processor import HuggingFaceProcessor
from ai.database.sales import SalesDatabase
from ai.ticketing import TicketingSystem
from security.ratelimiter import RateLimiter
from utils.cache import TTLCache
from config import Settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class TelegramMessage(BaseModel):
    """Pydantic model for telegram message validation"""
    message: Dict[str, Any]

    @property
    def user_id(self) -> str:
        return str(self.message.get("from", {}).get("id", ""))

    @property
    def text(self) -> str:
        return self.message.get("text", "")

class BotDependencies:
    """Dependency container for bot dependencies"""
    def __init__(self, settings: Settings):
        self.nlp = HuggingFaceProcessor()
        self.queue = RedisQueue()
        self.sales_db = SalesDatabase()
        self.ticketing = TicketingSystem()
        self.rate_limiter = RateLimiter()
        self.cache = TTLCache()
        self.settings = settings

@asynccontextmanager
async def get_bot(settings: Settings = Depends(Settings)) -> AsyncGenerator[TelegramBot, None]:
    """Async context manager for bot initialization"""
    try:
        deps = BotDependencies(settings)
        bot = TelegramBot(
            nlp=deps.nlp,
            queue=deps.queue,
            sales_db=deps.sales_db,
            ticketing=deps.ticketing,
            rate_limiter=deps.rate_limiter,
            cache=deps.cache,
        )
        yield bot
    except Exception as e:
        logger.error(f"Error initializing bot: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize bot services"
        )
    finally:
        # Cleanup resources
        await deps.queue.close()
        await deps.cache.close()

@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    bot: TelegramBot = Depends(get_bot)
) -> JSONResponse:
    """
    Handle incoming Telegram webhook requests
    
    Args:
        request (Request): FastAPI request object
        bot (TelegramBot): Bot instance from dependency injection
    
    Returns:
        JSONResponse: Response to telegram
    """
    try:
        body = await request.json()
        message = TelegramMessage(message=body.get("message", {}))

        if not message.user_id or not message.text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload: missing user_id or message text"
            )

        # Rate limiting check
        if not await bot.rate_limiter.check_limit(message.user_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Rate limit exceeded"}
            )

        # Process message
        try:
            response = await bot.process_message(message.user_id, message.text)
            return JSONResponse(content=response)
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Failed to process message"}
            )

    except ValidationError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message format"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/telegram/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}
