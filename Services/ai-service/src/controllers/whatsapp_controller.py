from fastapi import APIRouter
from services.whatsapp_service import WhatsAppService

router = APIRouter()

@router.post("/send-message")
async def send_whatsapp_message(phone: str, message: str):
    response = WhatsAppService.send_message(phone, message)
    return {"status": response}
    @router.post("/send-bulk-messages")
    async def send_bulk_messages(messages: list[dict]):
        """Send multiple WhatsApp messages in batch"""
        results = []
        for msg in messages:
            try:
                response = WhatsAppService.send_message(msg["phone"], msg["message"])
                results.append({"phone": msg["phone"], "status": response, "success": True})
            except Exception as e:
                results.append({"phone": msg["phone"], "status": str(e), "success": False})
        return {"results": results}

    @router.get("/message-status/{message_id}")
    async def get_message_status(message_id: str):
        """Check delivery status of a message"""
        try:
            status = WhatsAppService.get_message_status(message_id)
            return {"message_id": message_id, "status": status}
        except Exception as e:
            return {"message_id": message_id, "status": "error", "error": str(e)}

    @router.post("/send-template")
    async def send_template_message(phone: str, template_name: str, params: dict):
        """Send a template message with dynamic parameters"""
        try:
            response = WhatsAppService.send_template(phone, template_name, params)
            return {"status": response, "success": True}
        except Exception as e:
            return {"status": str(e), "success": False}