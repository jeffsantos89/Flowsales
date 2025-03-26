from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, Float, DateTime, String, JSON, text, ForeignKey
from sqlalchemy.orm import relationship, validates
from enum import Enum
from database import Base

class LogStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

class ForecastStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class AiLog(Base):
    """Model for tracking AI operations and their results."""
    __tablename__ = "ai_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default=LogStatus.PENDING.value)
    error_message = Column(String(500), nullable=True)
    processing_time = Column(Float, nullable=True)  # in seconds
    created_at = Column(DateTime, server_default=text('NOW()'), nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    @validates('model_name')
    def validate_model_name(self, key: str, value: str) -> str:
        if not value:
            raise ValueError("Model name cannot be empty")
        if len(value) > 100:
            raise ValueError("Model name must be less than 100 characters")
        return value

    @validates('status')
    def validate_status(self, key: str, value: str) -> str:
        if value not in [status.value for status in LogStatus]:
            raise ValueError(f"Invalid status. Must be one of {[status.value for status in LogStatus]}")
        return value

class SalesForecast(Base):
    """Model for storing sales forecasting predictions."""
    __tablename__ = "sales_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    predicted_sales = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=True)
    prediction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    forecast_period_start = Column(DateTime, nullable=False)
    forecast_period_end = Column(DateTime, nullable=False)
    status = Column(String(20), default=ForecastStatus.PENDING.value, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=text('NOW()'), nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relationship with products table (assuming it exists)
    product = relationship("Product", back_populates="forecasts")

    @validates('predicted_sales')
    def validate_predicted_sales(self, key: str, value: float) -> float:
        if value < 0:
            raise ValueError("Predicted sales cannot be negative")
        return value

    @validates('confidence_score')
    def validate_confidence_score(self, key: str, value: Optional[float]) -> Optional[float]:
        if value is not None and not (0 <= value <= 1):
            raise ValueError("Confidence score must be between 0 and 1")
        return value

    @validates('status')
    def validate_status(self, key: str, value: str) -> str:
        if value not in [status.value for status in ForecastStatus]:
            raise ValueError(f"Invalid status. Must be one of {[status.value for status in ForecastStatus]}")
        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'predicted_sales': self.predicted_sales,
            'confidence_score': self.confidence_score,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'forecast_period_start': self.forecast_period_start.isoformat() if self.forecast_period_start else None,
            'forecast_period_end': self.forecast_period_end.isoformat() if self.forecast_period_end else None,
            'status': self.status,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
