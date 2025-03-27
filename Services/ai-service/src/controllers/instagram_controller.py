from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field, validator
from typing import Protocol, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
from enum import Enum
from functools import lru_cache
from src.factories.bot_factory import bots
from logging import setup_logging

# Configuração de logging centralizada
logger = setup_logging()

class MessagePlatform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class MessageService(Protocol):
    @classmethod
    async def send_message(cls, recipient_id: str, message: str) -> dict:
        ...
    
    @classmethod
    async def comment_on_post(cls, post_id: str, message: str) -> dict:
        ...

class BaseRequest(BaseModel):
    class Config:
        use_enum_values = True
        extra = "forbid"
        validate_assignment = True

class MessageRequest(BaseRequest):
    message: str = Field(..., min_length=1, max_length=2000)
    platform: MessagePlatform

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty or only whitespace")
        return v.strip()

class CommentRequest(BaseRequest):
    post_id: str = Field(..., description="Post identifier")
    message: str = Field(..., min_length=1, max_length=2000)
    platform: MessagePlatform

class SocialMediaController:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        self.services: Dict[MessagePlatform, MessageService] = {
            MessagePlatform.INSTAGRAM: bots["instagram"],
            MessagePlatform.FACEBOOK: bots["facebook"]
        }

    def _setup_routes(self):
        @self.router.post("/{platform}/send-message")
        async def send_message(
            platform: MessagePlatform,
            request: MessageRequest,
            service: MessageService = Depends(self._get_service)
        ):
            try:
                logger.info(f"Sending message via {platform}")
                result = await service.send_message(
                    recipient_id=request.recipient_id,
                    message=request.message
                )
                return self._create_response(platform, "message_sent", result)
            except Exception as e:
                logger.error(f"Error in {platform} message: {str(e)}", exc_info=True)
                raise self._handle_error(e)

        @self.router.post("/{platform}/comment")
        async def comment_on_post(
            platform: MessagePlatform,
            request: CommentRequest,
            service: MessageService = Depends(self._get_service)
        ):
            try:
                logger.info(f"Commenting on post via {platform}")
                result = await service.comment_on_post(
                    post_id=request.post_id,
                    message=request.message
                )
                return self._create_response(platform, "comment_posted", result)
            except Exception as e:
                logger.error(f"Error in {platform} comment: {str(e)}", exc_info=True)
                raise self._handle_error(e)

    def _get_service(self, platform: MessagePlatform) -> MessageService:
        service = self.services.get(platform)
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service not found for platform: {platform}"
            )
        return service

    @staticmethod
    def _create_response(platform: MessagePlatform, action: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "platform": platform,
            "action": action,
            "result": result
        }

    @staticmethod
    def _handle_error(error: Exception) -> HTTPException:
        if isinstance(error, HTTPException):
            return error
        return HTTPException(
            status_code=500,
            detail=str(error)
        )

# Instância única do controlador
social_media_controller = SocialMediaController()
router = social_media_controller.router
