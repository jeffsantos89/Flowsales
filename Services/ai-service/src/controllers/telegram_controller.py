from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging
from src.factories.bot_factory import bots
from telegram_handler import TelegramService  # Assuming proper import path

# Configure logging with more detailed settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Request/Response models
class TelegramMessageRequest(BaseModel):
    chat_id: str = Field(..., description="Telegram chat identifier")
    message: str = Field(..., min_length=1, max_length=4096)
    disable_notification: Optional[bool] = Field(False, description="Send message silently")

class TelegramMessageResponse(BaseModel):
    status: str
    message_id: Optional[str]
    timestamp: datetime
    error: Optional[str] = None

# Single router instance
router = APIRouter(
    prefix="/telegram",
    tags=["Telegram Bot"],
    responses={
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"}
    }
)

@router.post(
    "/webhook",
    response_model=TelegramMessageResponse,
    status_code=status.HTTP_200_OK
)
async def telegram_webhook(req: Request) -> TelegramMessageResponse:
    """
    Handle incoming webhook requests from Telegram.
    """
    try:
        data = await req.json()
        chat_id = data.get("chat_id")
        message = data.get("message")

        if not chat_id or not message:
            raise ValueError("Invalid message data: chat_id and message are required")

        logger.info(f"Processing webhook request for chat_id: {chat_id}")
        response = await bots["telegram"].reply_to_user(chat_id, message)
        
        return TelegramMessageResponse(
            status="success",
            message_id=str(response.get("message_id")),
            timestamp=datetime.utcnow()
        )

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except KeyError as ke:
        logger.error(f"Bot configuration error: {str(ke)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail="Telegram bot configuration error")
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail="Internal server error")

@router.post(
    "/send-message",
    response_model=TelegramMessageResponse,
    status_code=status.HTTP_200_OK
)
async def send_telegram_message(
    message_request: TelegramMessageRequest
) -> TelegramMessageResponse:
    """
    Send a message through Telegram API.
    """
    try:
        logger.info(f"Sending message to chat_id: {message_request.chat_id}")
        response = await TelegramService.send_message(
            message_request.chat_id,
            message_request.message,
            disable_notification=message_request.disable_notification
        )
        
        return TelegramMessageResponse(
            status="success",
            message_id=str(response.get("message_id")),
            timestamp=datetime.utcnow()
        )
    
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error sending telegram message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )