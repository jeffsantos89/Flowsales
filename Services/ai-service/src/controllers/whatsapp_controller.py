from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel, validator
from services.whatsapp_service import WhatsAppService
from src.factories.bot_factory import bots
from logging import getLogger

logger = getLogger(__name__)

# Pydantic models for request validation
class Message(BaseModel):
    phone: str
    message: str

    @validator('phone')
    def validate_phone(cls, v):
        if not v.strip() or not v.replace('+', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v

class TemplateMessage(BaseModel):
    phone: str
    template_name: str
    params: Dict

class BulkMessages(BaseModel):
    messages: List[Message]

# Single router instance
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Bot"])

@router.post("/webhook")
async def whatsapp_webhook(req: Request):
    """Handle incoming webhook requests from WhatsApp"""
    try:
        data = await req.json()
        message_id = data.get("message_id")
        payload = data.get("payload")

        if not payload:
            raise ValueError("Missing payload")

        response = await bots["whatsapp"].send_message(payload=payload)
        return {
            "status": "success",
            "message_id": message_id,
            "response": response
        }

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/send-message", response_model=Dict)
async def send_whatsapp_message(message: Message):
    """Send a single WhatsApp message"""
    try:
        response = await WhatsAppService.send_message(message.phone, message.message)
        return {"status": "success", "response": response}
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-bulk-messages", response_model=Dict)
async def send_bulk_messages(request: BulkMessages):
    """Send multiple WhatsApp messages in batch"""
    results = []
    for msg in request.messages:
        try:
            response = await WhatsAppService.send_message(msg.phone, msg.message)
            results.append({
                "phone": msg.phone,
                "status": "success",
                "response": response
            })
        except Exception as e:
            logger.error(f"Error in bulk message: {str(e)}", exc_info=True)
            results.append({
                "phone": msg.phone,
                "status": "error",
                "error": str(e)
            })
    
    return {"results": results}

@router.get("/message-status/{message_id}")
async def get_message_status(message_id: str):
    """Check delivery status of a message"""
    try:
        status = await WhatsAppService.get_message_status(message_id)
        return {
            "message_id": message_id,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error getting message status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-template")
async def send_template_message(template: TemplateMessage):
    """Send a template message with dynamic parameters"""
    try:
        response = await WhatsAppService.send_template(
            template.phone,
            template.template_name,
            template.params
        )
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        logger.error(f"Error sending template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))