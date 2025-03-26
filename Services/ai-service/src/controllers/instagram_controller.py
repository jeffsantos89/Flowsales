# src/controllers/base_message_controller.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Protocol
from abc import ABC, abstractmethod
import logging
from enum import Enum

# Configuração de logging mais robusta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MessageService(Protocol):
    @classmethod
    async def send_message(cls, recipient_id: str, message: str) -> dict:
        ...

class MessagePlatform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class BaseMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    class Config:
        extra = "forbid"

class InstagramMessageRequest(BaseMessageRequest):
    user_id: str = Field(..., description="Instagram user identifier")
    platform: MessagePlatform = MessagePlatform.INSTAGRAM

class FacebookMessageRequest(BaseMessageRequest):
    recipient_id: str = Field(..., description="Facebook recipient ID")
    platform: MessagePlatform = MessagePlatform.FACEBOOK

class BaseMessageController:
    def __init__(self, service: MessageService, platform_name: str):
        self.service = service
        self.router = APIRouter(prefix=f"/{platform_name}", tags=[platform_name.capitalize()])
        self.logger = logging.getLogger(f"{platform_name}_controller")
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/send-message")
        async def send_message(request: BaseMessageRequest):
            try:
                recipient = getattr(request, 'user_id', None) or getattr(request, 'recipient_id', None)
                self.logger.info(f"Sending {request.platform.value} message to {recipient}")
                
                result = await self.service.send_message(recipient, request.message)
                
                return {
                    "status": "success",
                    "platform": request.platform.value,
                    "recipient": recipient,
                    "result": result
                }
            except Exception as e:
                self.logger.error(f"{request.platform.value} error: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"{request.platform.value} message failed: {str(e)}"
                )

# src/controllers/instagram_controller.py
from services.instagram_service import InstagramService

instagram_controller = BaseMessageController(
    service=InstagramService,
    platform_name="instagram"
).router

# src/controllers/facebook_controller.py
from services.facebook_service import FacebookService

facebook_controller = BaseMessageController(
    service=FacebookService,
    platform_name="facebook"
).router
