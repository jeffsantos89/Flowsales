# src/controllers/social_media_controller.py

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Literal, Dict, Optional
from abc import ABC, abstractmethod
from src.ai.chatbots.instagram.instagramBot import InstagramChatBot
from src.ai.chatbots.facebook.facebookBot import FacebookChatBot
from ..ai.queue.redis_backend import RedisQueue
from ..utils.logger import logger
from ..factories.bot_factory import bots
from ..config import settings

class WebhookRequest(BaseModel):
    sender: dict = Field(..., description="Sender information")
    message: dict = Field(..., description="Message content")

    @validator('sender')
    def validate_sender(cls, v):
        if not v.get('id'):
            raise ValueError("Sender ID is required")
        return v

    @validator('message')
    def validate_message(cls, v):
        if not v.get('text'):
            raise ValueError("Message text is required")
        return v

class SocialMediaMessageRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=4096)
    platform: Literal["facebook", "instagram"]
    metadata: Optional[dict] = Field(default=None, description="Additional message metadata")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "12345",
                "message": "Hello!",
                "platform": "facebook",
                "metadata": {"source": "web"}
            }
        }

class SocialMediaController(ABC):
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self._setup_rate_limiting()

    def _setup_rate_limiting(self):
        # Implement rate limiting logic here
        pass

    @abstractmethod
    async def platform_specific_validation(self, user_id: str, message: str):
        """Platform specific validation logic"""
        pass

    async def send_message(self, user_id: str, message: str, metadata: Optional[dict] = None):
        try:
            await self.platform_specific_validation(user_id, message)
            logger.info(f"[{self.__class__.__name__}] Sending message to user {user_id}")
            
            response = await self.bot.handle_message(
                user_id=user_id,
                message=message,
                metadata=metadata
            )
            
            return self._create_success_response(response)
        
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Error sending message: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": str(e), "timestamp": datetime.utcnow().isoformat()}
            )

    @staticmethod
    def _create_success_response(data):
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

class FacebookController(SocialMediaController):
    async def platform_specific_validation(self, user_id: str, message: str):
        if not user_id.isdigit():
            raise ValueError("Facebook user ID must be numeric")

class InstagramController(SocialMediaController):
    async def platform_specific_validation(self, user_id: str, message: str):
        if len(message) > 1000:  # Instagram-specific limit
            raise ValueError("Message exceeds Instagram character limit")

# Initialize core components
queue = RedisQueue()
controllers: Dict[str, SocialMediaController] = {
    "facebook": FacebookController(FacebookChatBot(queue=queue)),
    "instagram": InstagramController(InstagramChatBot(queue=queue))
}

# Router setup
router = APIRouter(prefix="/social", tags=["Social Media"])

@router.post("/webhook/{platform}")
async def social_media_webhook(platform: Literal["facebook", "instagram"], request: Request):
    try:
        data = await request.json()
        webhook_data = WebhookRequest(**data)
        
        controller = controllers.get(platform)
        if not controller:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

        response = await controller.send_message(
            user_id=webhook_data.sender['id'],
            message=webhook_data.message['text']
        )
        
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Webhook error for platform {platform}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/send-message")
async def send_social_media_message(request: SocialMediaMessageRequest):
    """
    Send a message through the specified social media platform.
    """
    try:
        controller = controllers.get(request.platform)
        if not controller:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {request.platform}"
            )
        
        return await controller.send_message(
            user_id=request.user_id,
            message=request.message,
            metadata=request.metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing {request.platform} message")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
