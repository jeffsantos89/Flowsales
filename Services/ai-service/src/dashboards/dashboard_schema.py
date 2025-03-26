from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal

class DashboardResponse(BaseModel):
    """
    Schema for dashboard analytics response.
    Contains key metrics and performance indicators.
    """
    total_users: int = Field(
        ...,
        description="Total number of registered users",
        gt=0
    )
    
    total_predictions: int = Field(
        ...,
        description="Total number of predictions made",
        gt=0
    )
    
    total_sales: Decimal = Field(
        ...,
        description="Total sales amount in the platform",
        gt=0,
        decimal_places=2
    )
    
    average_sale_value: Optional[Decimal] = Field(
        None,
        description="Average value per sale",
        decimal_places=2
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of when the metrics were calculated"
    )
    
    success_rate: Optional[float] = Field(
        None,
        description="Success rate of predictions",
        ge=0,
        le=100
    )

    @validator('average_sale_value', always=True)
    def calculate_average_sale(cls, v, values):
        """Calculate average sale value if not provided"""
        if v is None and values.get('total_sales') and values.get('total_predictions'):
            if values['total_predictions'] > 0:
                return Decimal(values['total_sales'] / values['total_predictions'])
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "total_users": 15000,
                "total_predictions": 24000,
                "total_sales": Decimal("78500.50"),
                "average_sale_value": Decimal("3.27"),
                "timestamp": datetime.utcnow(),
                "success_rate": 95.5
            }
        }
