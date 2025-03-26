# filepath: src/models/audit_log.py
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
from enum import Enum

Base = declarative_base()

class ActionType(Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"

class AuditLog(Base):
    """
    AuditLog model for tracking system activities and changes.
    Includes comprehensive logging capabilities with data validation.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    entity = Column(String(100), nullable=False)
    entity_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)
    status = Column(String(50), default="SUCCESS")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Create composite index for common queries
    __table_args__ = (
        Index('idx_audit_entity_id', 'entity', 'entity_id'),
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_user', 'user_id'),
    )

    @validates('action')
    def validate_action(self, key: str, action: str) -> str:
        """Validate that the action is one of the predefined types."""
        try:
            return ActionType[action].value
        except KeyError:
            raise ValueError(f"Invalid action type: {action}")

    @validates('ip_address')
    def validate_ip(self, key: str, ip: Optional[str]) -> Optional[str]:
        """Validate IP address format."""
        if ip and len(ip) > 45:
            raise ValueError("IP address too long")
        return ip

    def to_dict(self) -> Dict[str, Any]:
        """Convert the audit log entry to a dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action': self.action,
            'entity': self.entity,
            'entity_id': self.entity_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': self.details,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return (
            f"<AuditLog("
            f"id={self.id}, "
            f"action='{self.action}', "
            f"entity='{self.entity}', "
            f"entity_id='{self.entity_id}', "
            f"user_id='{self.user_id}', "
            f"timestamp='{self.timestamp}')"
        )