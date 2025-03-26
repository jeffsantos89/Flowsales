from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Enum, Index
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base
import uuid
import enum
from dataclasses import dataclass
from typing import ClassVar

Base = declarative_base()

class AILogStatus(enum.Enum):
    """Enumeration for possible AI Log statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AILogConfig:
    """Configuration constants for AILog"""
    MAX_SERVICE_NAME_LENGTH: ClassVar[int] = 100
    MAX_REQUEST_TYPE_LENGTH: ClassVar[int] = 50
    MAX_USER_ID_LENGTH: ClassVar[int] = 100
    TRACE_ID_LENGTH: ClassVar[int] = 36

class AILog(Base):
    """
    AI Log model for tracking AI operations and responses with enhanced features
    and optimized database indexing
    """
    __tablename__ = "ai_logs"

    # Primary and tracking fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(
        String(AILogConfig.TRACE_ID_LENGTH), 
        unique=True, 
        nullable=False, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Core fields with proper length constraints
    user_id = Column(String(AILogConfig.MAX_USER_ID_LENGTH), nullable=True)
    service_name = Column(String(AILogConfig.MAX_SERVICE_NAME_LENGTH), nullable=False)
    request_type = Column(String(AILogConfig.MAX_REQUEST_TYPE_LENGTH), nullable=False)
    
    # Data fields
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Integer, nullable=True)
    
    # Status and timestamp fields
    status = Column(
        Enum(AILogStatus), 
        nullable=False, 
        default=AILogStatus.PENDING
    )
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Optimized composite indexes
    __table_args__ = (
        Index('idx_service_status_created', 'service_name', 'status', 'created_at'),
        Index('idx_user_service', 'user_id', 'service_name'),
        Index('idx_status_created', 'status', 'created_at'),
    )

    @validates('status')
    def validate_status(self, key: str, status: AILogStatus) -> AILogStatus:
        """Validate status field ensuring type safety"""
        if not isinstance(status, AILogStatus):
            try:
                return AILogStatus(status)
            except ValueError:
                raise ValueError(f"Invalid status. Must be one of: {[s.value for s in AILogStatus]}")
        return status

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary with proper type handling"""
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "user_id": self.user_id,
            "service_name": self.service_name,
            "request_type": self.request_type,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def create_log(cls, 
                  service_name: str, 
                  request_type: str, 
                  input_data: Dict[str, Any], 
                  user_id: Optional[str] = None) -> "AILog":
        """Factory method to create a new log entry with validation"""
        if not service_name or not request_type:
            raise ValueError("service_name and request_type are required")
        
        return cls(
            service_name=service_name,
            request_type=request_type,
            input_data=input_data,
            user_id=user_id,
            status=AILogStatus.PENDING
        )

    def update_completion(self, output_data: Dict[str, Any], processing_time: int) -> None:
        """Update log with completion data and validate processing time"""
        if processing_time < 0:
            raise ValueError("processing_time must be non-negative")
        
        self.output_data = output_data
        self.processing_time = processing_time
        self.status = AILogStatus.COMPLETED

    def update_failure(self, error_message: str) -> None:
        """Update log with failure information"""
        if not error_message:
            error_message = "Unknown error occurred"
        
        self.error_message = error_message
        self.status = AILogStatus.FAILED

    def start_processing(self) -> None:
        """Mark the log as processing"""
        self.status = AILogStatus.PROCESSING

    def __repr__(self) -> str:
        """String representation of the log entry"""
        return (
            f"<AILog("
            f"id={self.id}, "
            f"trace_id={self.trace_id}, "
            f"status={self.status.value}, "
            f"service={self.service_name}"
            f")>"
        )
