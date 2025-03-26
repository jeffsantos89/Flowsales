from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean, JSON
from sqlalchemy.orm import relationship, validates, declared_attr
from sqlalchemy.ext.declarative import declared_attr
from database.db_base import Base
from datetime import datetime
import enum
from typing import Optional, Dict, Any, Union, List
import re
from uuid import uuid4
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

class BaseEnum(enum.Enum):
    """Base class for all enums with common functionality"""
    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls]

    @classmethod
    def members(cls) -> List[str]:
        return [member.name for member in cls]

    @classmethod
    def contains(cls, value: str) -> bool:
        return value in cls.values()

class BaseMixin:
    """Base mixin with common attributes and methods for all models"""
    @declared_attr
    def __tablename__(cls) -> str:
        """Automatically generate table name from class name"""
        return cls.__name__.lower() + 's'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid4()), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    @classmethod
    def get_by_uuid(cls, db_session, uuid: str) -> Optional['BaseMixin']:
        """Get model instance by UUID"""
        return db_session.query(cls).filter(cls.uuid == uuid, cls.is_active == True).first()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {column.name: getattr(self, column.name)
                for column in self.__table__.columns}

class UserStatus(BaseEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class ModelType(BaseEnum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    TIME_SERIES = "time_series"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"

class User(Base, BaseMixin):
    """User model with enhanced security and validation"""
    name = Column(String(100), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")

    @validates('email')
    def validate_email(self, key: str, email: str) -> str:
        if not email:
            raise ValueError("Email is required")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError("Invalid email format")
        return email.lower()

    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        if not name or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return name.strip()

    @hybrid_property
    def is_active_user(self) -> bool:
        return self.status == UserStatus.ACTIVE and self.is_verified

    def increment_failed_login(self) -> None:
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.status = UserStatus.SUSPENDED

    def reset_failed_login(self) -> None:
        self.failed_login_attempts = 0
        self.last_login = datetime.utcnow()

class Prediction(Base, BaseMixin):
    """Prediction model with enhanced validation and metadata handling"""
    model_name = Column(String(100), index=True, nullable=False)
    model_type = Column(Enum(ModelType), nullable=False)
    prediction_value = Column(Float, nullable=False)
    confidence_score = Column(Float)
    metadata = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="predictions")
    sales = relationship("SalesData", back_populates="prediction", cascade="all, delete-orphan")

    @validates('confidence_score')
    def validate_confidence_score(self, key: str, score: Optional[float]) -> Optional[float]:
        if score is not None and not (0 <= score <= 1):
            raise ValueError("Confidence score must be between 0 and 1")
        return score

    @validates('model_name')
    def validate_model_name(self, key: str, name: str) -> str:
        if not name or len(name.strip()) < 1:
            raise ValueError("Model name cannot be empty")
        return name.strip()

class SalesData(Base, BaseMixin):
    """Sales data model with enhanced validation and calculations"""
    product_name = Column(String(255), index=True, nullable=False)
    revenue = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    category = Column(String(100), nullable=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    prediction_id = Column(Integer, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False)
    prediction = relationship("Prediction", back_populates="sales")

    @validates('revenue', 'quantity')
    def validate_positive_numbers(self, key: str, value: Union[float, int]) -> Union[float, int]:
        if value < 0:
            raise ValueError(f"{key.capitalize()} cannot be negative")
        return value

    @validates('product_name')
    def validate_product_name(self, key: str, name: str) -> str:
        if not name or len(name.strip()) < 1:
            raise ValueError("Product name cannot be empty")
        return name.strip()

    @hybrid_property
    def unit_price(self) -> float:
        """Calculate unit price from revenue and quantity"""
        return self.revenue / self.quantity if self.quantity else 0

    @hybrid_property
    def total_value(self) -> float:
        """Calculate total value of the sale"""
        return self.revenue
