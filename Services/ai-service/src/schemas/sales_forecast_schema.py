from pydantic import BaseModel, Field, validator
from datetime import date, timedelta
from typing import Optional, List
from decimal import Decimal
from uuid import UUID

class SalesForecastRequest(BaseModel):
    product_id: UUID = Field(..., description="Unique identifier for the product")
    start_date: date = Field(..., description="Start date for the forecast period")
    end_date: date = Field(..., description="End date for the forecast period")
    include_confidence_intervals: bool = Field(default=True, description="Whether to include confidence intervals in the response")
    granularity: str = Field(default="daily", description="Forecast granularity: daily, weekly, or monthly")

    @validator('end_date')
    def validate_date_range(cls, end_date, values):
        if 'start_date' in values and end_date <= values['start_date']:
            raise ValueError("end_date must be after start_date")
        if 'start_date' in values and (end_date - values['start_date']) > timedelta(days=365):
            raise ValueError("Forecast period cannot exceed 1 year")
        return end_date

    class Config:
        schema_extra = {
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "include_confidence_intervals": True,
                "granularity": "monthly"
            }
        }

class ForecastPoint(BaseModel):
    date: date
    predicted_value: Decimal = Field(..., ge=0, decimal_places=2)
    lower_bound: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    upper_bound: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

class SalesForecastResponse(BaseModel):
    product_id: UUID
    forecasts: List[ForecastPoint]
    model_version: str = Field(..., description="Version of the forecasting model used")
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence level for the intervals")
    created_at: date = Field(default_factory=date.today)
    metadata: Optional[dict] = Field(None, description="Additional forecast metadata")

    class Config:
        schema_extra = {
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "forecasts": [
                    {
                        "date": "2023-01-01",
                        "predicted_value": "100.00",
                        "lower_bound": "90.00",
                        "upper_bound": "110.00"
                    }
                ],
                "model_version": "1.0.0",
                "confidence_level": 0.95,
                "created_at": "2023-01-01",
                "metadata": {"algorithm": "Prophet"}
            }
        }
