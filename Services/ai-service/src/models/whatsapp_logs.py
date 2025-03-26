from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declared_attr
from database import Base
from datetime import datetime
import enum
from typing import Optional
from uuid import uuid4

class MessageStatus(enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class MessageType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"

class BaseModel:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class WhatsAppLog(BaseModel, Base):
    """
    WhatsApp message logging model with enhanced features and validation
    """
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), nullable=False, default=MessageType.TEXT)
    status = Column(Enum(MessageStatus), nullable=False, default=MessageStatus.SENT)
    recipient_phone = Column(String(20), nullable=False, index=True)
    message_id = Column(String(64), unique=True, index=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="whatsapp_logs")

    @validates('recipient_phone')
    def validate_phone(self, key, phone):
        if not phone or len(phone) < 10:
            raise ValueError("Invalid phone number")
        return phone

    @validates('message')
    def validate_message(self, key, message):
        if not message or len(message.strip()) == 0:
            raise ValueError("Message cannot be empty")
        return message

    def __repr__(self) -> str:
        return f"<WhatsAppLog(id={self.id}, user_id={self.user_id}, status={self.status})>"

    @property
    def is_delivered(self) -> bool:
        return self.status == MessageStatus.DELIVERED

    @property
    def is_failed(self) -> bool:
        return self.status == MessageStatus.FAILED

    def update_status(self, new_status: MessageStatus, error: Optional[str] = None) -> None:
        self.status = new_status
        if error:
            self.error_message = error
        self.updated_at = datetime.utcnow()
