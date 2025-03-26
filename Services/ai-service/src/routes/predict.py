from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from pathlib import Path
import logging
import joblib
import traceback
from datetime import datetime
from functools import lru_cache

from core.config import Settings
from schemas.predict_schema import (
    LeadFeatures, LeadScoringResponse,
    ChurnFeatures, ChurnResponse
)
from database import get_db
from models.ai_logs import AiLog
from services.model_service import ModelService
from core.logger import setup_logger

# Configure logging
logger = setup_logger(__name__)

class PredictionRouter:
    def __init__(self, settings: Settings):
        self.router = APIRouter(prefix="/v1/predictions", tags=["predictions"])
        self.settings = settings
        self.model_service = ModelService()
        self._setup_routes()

    @lru_cache()
    def _load_model(self, model_path: str):
        """Load ML model with caching"""
        try:
            return joblib.load(model_path)
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model loading failed"
            )

    def _log_prediction(
        self, 
        db: Session, 
        model_name: str, 
        input_data: Dict[str, Any], 
        output_data: Dict[str, Any]
    ) -> AiLog:
        """Log prediction to database"""
        try:
            new_log = AiLog(
                model_name=model_name,
                input_data=input_data,
                output_data=output_data,
                created_at=datetime.utcnow()
            )
            db.add(new_log)
            db.commit()
            db.refresh(new_log)
            return new_log
        except Exception as e:
            logger.error(f"Failed to log prediction: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log prediction"
            )

    async def predict_lead_scoring(
        self, 
        features: LeadFeatures, 
        db: Session = Depends(get_db)
    ) -> LeadScoringResponse:
        """Predict lead score with error handling and logging"""
        try:
            model = self._load_model(self.settings.LEAD_MODEL_PATH)
            
            # Input validation and preprocessing
            X = self.model_service.preprocess_lead_features([features])
            
            # Make prediction
            score = float(model.predict(X)[0])
            
            # Validate prediction
            if not 0 <= score <= 1:
                raise ValueError("Invalid prediction value")

            # Log prediction
            log = self._log_prediction(
                db=db,
                model_name="lead_scoring",
                input_data=features.dict(),
                output_data={"score": score}
            )

            return LeadScoringResponse(logId=log.id, score=score)

        except Exception as e:
            logger.error(f"Lead scoring prediction failed: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def predict_churn(
        self, 
        features: ChurnFeatures, 
        db: Session = Depends(get_db)
    ) -> ChurnResponse:
        """Predict churn probability with error handling and logging"""
        try:
            model = self._load_model(self.settings.CHURN_MODEL_PATH)
            
            # Input validation and preprocessing
            X = self.model_service.preprocess_churn_features([features])
            
            # Make prediction
            churn_prob = float(model.predict_proba(X)[0][1])
            
            # Log prediction
            log = self._log_prediction(
                db=db,
                model_name="churn",
                input_data=features.dict(),
                output_data={"churn_probability": churn_prob}
            )

            return ChurnResponse(logId=log.id, churn_probability=churn_prob)

        except Exception as e:
            logger.error(f"Churn prediction failed: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def _setup_routes(self):
        """Setup router endpoints"""
        self.router.add_api_route(
            "/lead-scoring",
            self.predict_lead_scoring,
            methods=["POST"],
            response_model=LeadScoringResponse,
            summary="Predict lead score",
            description="Predict the likelihood of a lead converting"
        )
        
        self.router.add_api_route(
            "/churn",
            self.predict_churn,
            methods=["POST"],
            response_model=ChurnResponse,
            summary="Predict churn probability",
            description="Predict the likelihood of customer churn"
        )

# Initialize router
prediction_router = PredictionRouter(Settings()).router
