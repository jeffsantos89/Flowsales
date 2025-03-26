from pydantic import BaseModel
from datetime import datetime

class WhatsappMessage(BaseModel):
    user_id: str
    message: str
    phone: str
    timestamp: datetime
    message_type: str = "text"
    media_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str = "pending"
    metadata: dict | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "123456789",
                "message": "Hello World",
                "phone": "+5511999999999",
                "timestamp": "2024-01-01T00:00:00",
                "message_type": "text",
                "status": "pending"
            }
        }