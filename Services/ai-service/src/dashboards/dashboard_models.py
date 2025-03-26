from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from database.db_base import Base
import enum

class MetricType(enum.Enum):
    SALES = "sales"
    REVENUE = "revenue"
    CONVERSION = "conversion"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class BaseMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    @validates('value')
    def validate_value(self, key, value):
        if value is None:
            raise ValueError(f"{key} cannot be None")
        return value

class DashboardMetrics(Base, BaseMixin):
    __tablename__ = "dashboard_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, default=0, nullable=False)
    metric_type = Column(Enum(MetricType), nullable=False)
    description = Column(String(255))
    
    __table_args__ = (
        UniqueConstraint('metric_name', 'metric_type', name='uix_metric_name_type'),
    )

    @hybrid_property
    def is_positive(self) -> bool:
        return self.value > 0

    def __repr__(self) -> str:
        return f"<DashboardMetric(name={self.metric_name}, value={self.value}, type={self.metric_type})>"

class PredictionMetrics(Base, BaseMixin):
    __tablename__ = "prediction_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_count = Column(Integer, default=0, nullable=False)
    accuracy = Column(Float, default=0.0, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_prediction_at = Column(DateTime)
    
    user = relationship(
        "User",
        back_populates="predictions",
        lazy="joined"
    )

    @validates('prediction_count')
    def validate_prediction_count(self, key, value):
        if value < 0:
            raise ValueError("Prediction count cannot be negative")
        return value

    @validates('accuracy')
    def validate_accuracy(self, key, value):
        if not 0 <= value <= 1:
            raise ValueError("Accuracy must be between 0 and 1")
        return value

    def __repr__(self) -> str:
        return f"<PredictionMetrics(user_id={self.user_id}, count={self.prediction_count}, accuracy={self.accuracy})>"

