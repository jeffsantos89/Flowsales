# src/controllers/social_media_controller.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Dict, Type
from abc import ABC
from ai.chatbots.instagramBot import InstagramChatBot
from ai.chatbots.facebookBot import FacebookChatBot
from ai.queue.redis_backend import RedisQueue
from ai.utils.logger import logger

# Base message request model
class SocialMediaMessageRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=4096)
    platform: Literal["facebook", "instagram"]

# Base controller class
class SocialMediaController(ABC):
    def __init__(self, bot_instance):
        self.bot = bot_instance
        
    async def send_message(self, user_id: str, message: str):
        try:
            logger.info(f"[{self.__class__.__name__}] Message for user {user_id}")
            response = await self.bot.handle_message(user_id, message)
            return self._create_success_response(response)
        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Error sending message: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @staticmethod
    def _create_success_response(data):
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

# Platform specific controllers
class FacebookController(SocialMediaController):
    pass

class InstagramController(SocialMediaController):
    pass

# Router setup
router = APIRouter(tags=["Social Media"])

# Initialize queue and controllers
queue = RedisQueue()
controllers: Dict[str, SocialMediaController] = {
    "facebook": FacebookController(FacebookChatBot(queue=queue)),
    "instagram": InstagramController(InstagramChatBot(queue=queue))
}

@router.post("/send-message")
async def send_social_media_message(request: SocialMediaMessageRequest):
    """
    Send a message through the specified social media platform.
    
    Args:
        request (SocialMediaMessageRequest): The message request containing platform, user_id, and message
    
    Returns:
        dict: Response containing status, data, and timestamp
    
    Raises:
        HTTPException: If platform is not supported or message sending fails
    """
    try:
        controller = controllers.get(request.platform)
        if not controller:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {request.platform}"
            )
        
        return await controller.send_message(request.user_id, request.message)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing {request.platform} message")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
