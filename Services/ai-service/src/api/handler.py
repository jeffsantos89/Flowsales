from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel, ValidationError, Field
from datetime import datetime
from typing import Optional, Dict, Any
from functools import lru_cache
from contextlib import asynccontextmanager
from uuid import uuid4

# Core imports
from config.settings import Settings
from ai.llm.llm_provider import OpenAIProvider
from ai.chatbots.telegram.telegramBot import TelegramChatBot
from ai.queue.redis_backend import RedisQueueBackend
from utils.telemetry.setup_telemetry import setup_telemetry
from utils.rate_limiter import RateLimiter
from utils.jwt_manager import extract_user_id_from_token
from utils.logger import logger

# Custom exceptions
class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Enhanced models with validation
class ChatQuery(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=4000)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "Olá, preciso de ajuda!",
                "metadata": {"source": "web"},
                "session_id": "sess_abc"
            }
        }

class ChatResponse(BaseModel):
    response: str
    status: str
    request_id: str = Field(default_factory=lambda: f"req-{uuid4()}")
    correlation_id: Optional[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Application state management
class AppState:
    def __init__(self):
        self.llm: Optional[OpenAIProvider] = None
        self.queue: Optional[RedisQueueBackend] = None
        self.bot: Optional[TelegramChatBot] = None
        self.rate_limiter: Optional[RateLimiter] = None

    async def initialize(self, settings: Settings):
        try:
            self.llm = OpenAIProvider(api_key=settings.openai_api_key)
            self.queue = RedisQueueBackend(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password
            )
            self.bot = TelegramChatBot(
                api_token=settings.telegram_token,
                llm_provider=self.llm
            )
            self.rate_limiter = RateLimiter(
                redis_client=self.queue.client,
                max_requests=settings.rate_limit_max_requests,
                window_seconds=settings.rate_limit_window
            )
            await self.queue.connect()
            await self.bot.initialize()
            logger.info("Services initialized successfully")
        except Exception as e:
            logger.error(f"Service initialization failed: {str(e)}")
            raise AIServiceError("Failed to initialize services")

    async def cleanup(self):
        try:
            if self.queue:
                await self.queue.disconnect()
            if self.bot:
                await self.bot.cleanup()
            logger.info("Services cleaned up successfully")
        except Exception as e:
            logger.error(f"Service cleanup failed: {str(e)}")

app_state = AppState()

# Settings management
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await app_state.initialize(settings)
    try:
        yield
    finally:
        await app_state.cleanup()

# FastAPI application setup
app = FastAPI(
    title="Flowsale AI Service",
    version="1.0.0",
    description="AI Service Platform for Flowsale",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
async def verify_rate_limit(user_id: str):
    if not app_state.rate_limiter or not await app_state.rate_limiter.is_allowed(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

# Router setup with dependency injection
router = APIRouter(prefix="/api/v1", tags=["Chatbot"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: Request,
    data: ChatQuery,
    settings: Settings = Depends(get_settings)
):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
    
    try:
        await verify_rate_limit(data.user_id)
        logger.info(f"[{correlation_id}] Processing request from {data.user_id}")

        response_text = await app_state.bot.handle_customer_query(
            user_id=data.user_id,
            query=data.message,
            metadata=data.metadata
        )

        # Async analytics logging
        await app_state.queue.push("analytics", {
            "user_id": data.user_id,
            "timestamp": str(data.timestamp),
            "correlation_id": correlation_id,
            "success": True,
            "metadata": data.metadata
        })

        return ChatResponse(
            response=response_text,
            status="success",
            correlation_id=correlation_id
        )

    except ValidationError as e:
        logger.warning(f"[{correlation_id}] Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except AIServiceError as e:
        logger.error(f"[{correlation_id}] Service error: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"[{correlation_id}] Unexpected error: {str(e)}")
        await app_state.queue.push("errors", {
            "user_id": data.user_id,
            "error": str(e),
            "correlation_id": correlation_id,
            "timestamp": str(datetime.utcnow())
        })
        raise HTTPException(status_code=500, detail="Internal server error")

# Register routes
app.include_router(router)
