from pydantic import BaseModel
from datetime import datetime

class MarketplaceMessage(BaseModel):
    order_id: str
    customer_id: str
    message: str
    created_at: datetime
    updated_at: datetime | None = None
    status: str = "pending"
    message_type: str
    priority: int = 1
    metadata: dict | None = None
    
    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "order_id": "123456",
                "customer_id": "789012",
                "message": "Order confirmation",
                "message_type": "notification",
                "created_at": "2023-01-01T00:00:00",
                "status": "pending",
                "priority": 1,
                "metadata": {"source": "marketplace", "platform": "shopify"}
            }
        }