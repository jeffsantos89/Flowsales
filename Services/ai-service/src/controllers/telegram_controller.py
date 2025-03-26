from fastapi import APIRouter
from services.telegram_service import TelegramService
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging

router = APIRouter()

@router.post("/telegram/send-message")
async def send_telegram_message(chat_id: str, message: str):
    response = TelegramService.send_message(chat_id, message)
    return {"status": response}
    # Configure logging
    logging.basicConfig(level=logging.INFO)
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

    @router.post(
        "/telegram/send-message",
        response_model=TelegramMessageResponse,
        status_code=status.HTTP_200_OK,
        responses={
            400: {"description": "Bad Request"},
            500: {"description": "Internal Server Error"}
        }
    )
    async def send_telegram_message(message_request: TelegramMessageRequest):
        try:
            logger.info(f"Sending message to chat_id: {message_request.chat_id}")
            response = TelegramService.send_message(
                message_request.chat_id,
                message_request.message,
                disable_notification=message_request.disable_notification
            )
            
            return TelegramMessageResponse(
                status="success",
                message_id=response.get("message_id"),
                timestamp=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"Error sending telegram message: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )