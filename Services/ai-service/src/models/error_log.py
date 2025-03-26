from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import validates

Base = declarative_base()

class ErrorLog(Base):
    """
    Model for storing application error logs.
    
    Attributes:
        id (int): Unique identifier for the error log
        timestamp (datetime): When the error occurred
        error_type (str): Type/classification of the error
        message (str): Error message
        stack_trace (str): Full stack trace of the error
        severity (str): Error severity level
        environment (str): Environment where error occurred
        metadata (str): Additional JSON-serialized context data
    """
    
    __tablename__ = "error_logs"

    # Primary fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    error_type = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    severity = Column(String(50), nullable=False, default='ERROR')
    environment = Column(String(50), nullable=False)
    metadata = Column(Text)

    # Indexes for better query performance
    __table_args__ = (
        Index('ix_error_logs_timestamp', 'timestamp'),
        Index('ix_error_logs_error_type', 'error_type'),
        Index('ix_error_logs_severity', 'severity'),
    )

    # Valid severity levels
    SEVERITY_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    @validates('severity')
    def validate_severity(self, key: str, severity: str) -> str:
        """Validate severity level."""
        if severity.upper() not in self.SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity level. Must be one of {self.SEVERITY_LEVELS}")
        return severity.upper()

    @validates('error_type')
    def validate_error_type(self, key: str, error_type: str) -> str:
        """Validate error_type length."""
        if len(error_type) > 255:
            raise ValueError("error_type must not exceed 255 characters")
        return error_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert error log to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'error_type': self.error_type,
            'message': self.message,
            'stack_trace': self.stack_trace,
            'severity': self.severity,
            'environment': self.environment,
            'metadata': self.metadata
        }

    @classmethod
    def create(cls, 
               error_type: str, 
               message: str, 
               stack_trace: Optional[str] = None,
               severity: str = 'ERROR',
               environment: str = 'production',
               metadata: Optional[str] = None) -> 'ErrorLog':
        """Factory method to create new error log instance."""
        return cls(
            error_type=error_type,
            message=message,
            stack_trace=stack_trace,
            severity=severity,
            environment=environment,
            metadata=metadata
        )

    def __repr__(self) -> str:
        """String representation of the error log."""
        return (f"<ErrorLog(id={self.id}, timestamp={self.timestamp}, "
                f"error_type='{self.error_type}', severity='{self.severity}')>")