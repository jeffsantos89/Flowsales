from pydantic import BaseModel # type: ignore

class LeadFeatures(BaseModel):
    website_visits: int
    clicks: int

class LeadScoringResponse(BaseModel):
    logId: int
    score: float

class ChurnFeatures(BaseModel):
    usage: float
    complaints: int

class ChurnResponse(BaseModel):
    logId: int
    churn_probability: float

class ModelMetadata(BaseModel):
    model_version: str
    timestamp: str
    confidence_score: float

class ErrorResponse(BaseModel):
    error_code: int
    message: str
    details: dict | None = None

class HealthCheckResponse(BaseModel):
    status: str
    uptime: float
    model_status: dict

class PredictionBase(BaseModel):
    request_id: str
    client_id: str | None = None
    timestamp: str
    metadata: ModelMetadata | None = None

class LeadScoringRequest(PredictionBase, LeadFeatures):
    pass

class ChurnPredictionRequest(PredictionBase, ChurnFeatures):
    pass

class Config:
    schema_extra = {
        "example": {
            "request_id": "123e4567-e89b-12d3-a456-426614174000",
            "client_id": "client123",
            "timestamp": "2023-07-21T10:00:00Z"
        }
    }