from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from sqlalchemy.sql import func

Base = declarative_base()

class SocialMediaLog(Base):
    """
    Model for storing social media interaction logs.
    
    Attributes:
        id (int): Primary key for the log entry
        timestamp (datetime): When the interaction occurred
        user_id (int): Reference to the user who performed the action
        platform (str): Social media platform identifier
        message (str): Content of the interaction
        message_type (str): Type of interaction (e.g., 'post', 'comment', 'like')
        metadata (dict): Additional platform-specific data
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = "social_media_logs"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False)
    metadata = Column(JSON, default={})

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_social_media_logs_user_platform', 'user_id', 'platform'),
        Index('idx_social_media_logs_timestamp', 'timestamp'),
    )

    # Valid platforms and message types
    VALID_PLATFORMS = {'facebook', 'twitter', 'instagram', 'linkedin'}
    VALID_MESSAGE_TYPES = {'post', 'comment', 'like', 'share', 'message'}

    @validates('platform')
    def validate_platform(self, key: str, platform: str) -> str:
        """Validate the platform value."""
        if platform.lower() not in self.VALID_PLATFORMS:
            raise ValueError(f"Invalid platform. Must be one of: {', '.join(self.VALID_PLATFORMS)}")
        return platform.lower()

    @validates('message_type')
    def validate_message_type(self, key: str, message_type: str) -> str:
        """Validate the message type value."""
        if message_type.lower() not in self.VALID_MESSAGE_TYPES:
            raise ValueError(f"Invalid message type. Must be one of: {', '.join(self.VALID_MESSAGE_TYPES)}")
        return message_type.lower()

    @validates('metadata')
    def validate_metadata(self, key: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ensure metadata is always a dictionary."""
        return metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_id': self.user_id,
            'platform': self.platform,
            'message': self.message,
            'message_type': self.message_type,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        """String representation of the model."""
        return (
            f"<SocialMediaLog("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"platform='{self.platform}', "
            f"message_type='{self.message_type}'"
            f")>"
        )