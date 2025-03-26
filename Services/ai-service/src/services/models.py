from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, root_validator
from decimal import Decimal
from dataclasses import dataclass
from abc import ABC, abstractmethod

class ModelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"
    ERROR = "error"
    TRAINING = "training"
    EVALUATING = "evaluating"

class ModelType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"
    VIDEO = "video"
    TIMESERIES = "timeseries"

class ModelFramework(str, Enum):
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SCIKIT = "scikit-learn"
    CUSTOM = "custom"

class BaseModelSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    status: ModelStatus = Field(default=ModelStatus.PENDING)
    version_history: List[Dict] = Field(default_factory=list)

    class Config:
        orm_mode = True
        validate_assignment = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }

    def update_version_history(self, change_description: str) -> None:
        self.version_history.append({
            "timestamp": datetime.utcnow(),
            "change": change_description,
            "status": self.status
        })

class AIModel(BaseModelSchema):
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., regex=r"^\d+\.\d+\.\d+$")
    model_type: ModelType
    framework: ModelFramework = Field(default=ModelFramework.CUSTOM)
    description: Optional[str] = Field(None, max_length=500)
    parameters: Dict = Field(default_factory=dict)
    metrics: Dict = Field(default_factory=dict)
    metadata: Dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    resource_requirements: Dict = Field(default_factory=dict)
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        return datetime.utcnow()

    @root_validator
    def validate_metrics(cls, values):
        metrics = values.get('metrics', {})
        required_metrics = {'accuracy', 'precision', 'recall', 'f1_score'}
        if metrics and not all(metric in metrics for metric in required_metrics):
            raise ValueError(f"Missing required metrics: {required_metrics}")
        return values

class ModelResponse(BaseModelSchema):
    input_data: Dict
    output_data: Dict
    processing_time: Decimal = Field(..., decimal_places=6)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    model_id: UUID
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("Confidence score must be between 0 and 1")
        return v

    @root_validator
    def validate_processing_time(cls, values):
        if values.get('processing_time', 0) < 0:
            raise ValueError("Processing time cannot be negative")
        return values

class ModelBatch(BaseModelSchema):
    batch_size: int = Field(..., gt=0)
    models: List[AIModel]
    total_processing_time: Decimal = Field(..., decimal_places=6)
    success_rate: float = Field(..., ge=0.0, le=1.0)
    failed_items: List[Dict] = Field(default_factory=list)
    batch_metadata: Dict = Field(default_factory=dict)

    @root_validator
    def validate_batch(cls, values):
        models = values.get('models', [])
        batch_size = values.get('batch_size', 0)
        if len(models) > batch_size:
            raise ValueError("Number of models exceeds batch size")
        return values