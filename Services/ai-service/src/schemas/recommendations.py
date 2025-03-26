from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID

class RecommendationType(str, Enum):
    """Enum para tipos de recomendações permitidos"""
    PRODUCT = "product"
    CATEGORY = "category"
    PERSONALIZED = "personalized"
    TRENDING = "trending"
    SEASONAL = "seasonal"

class RecommendationResponse(BaseModel):
    """
    Modelo de resposta para recomendações.
    
    Attributes:
        id (UUID): Identificador único universal
        user_id (int): ID do usuário
        recommendation_type (RecommendationType): Tipo de recomendação
        content (str): Conteúdo da recomendação
        created_at (datetime): Data de criação
        updated_at (datetime): Data de atualização
        active (bool): Status da recomendação
        score (float): Pontuação da recomendação
        metadata (dict): Metadados adicionais
    """
    id: UUID = Field(..., description="Identificador único universal")
    user_id: int = Field(..., gt=0, description="ID do usuário")
    recommendation_type: RecommendationType
    content: str = Field(..., min_length=1, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    active: bool = Field(default=True)
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict)

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('content cannot be empty or only whitespace')
        return v.strip()

    @validator('updated_at')
    def validate_updated_at(cls, v, values):
        if v and v < values['created_at']:
            raise ValueError('updated_at cannot be earlier than created_at')
        return v

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": 1,
                "recommendation_type": "PRODUCT",
                "content": "Product recommendation content",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": None,
                "active": True,
                "score": 0.95,
                "metadata": {"source": "ai_model_v1"}
            }
        }