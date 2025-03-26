from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from services.predict_service import PredictService
from schemas.predict_schema import PredictRequest, PredictResponse
import logging
from core.exceptions import ModelPredictionError
from core.logging_config import setup_logger

# Configure logging
logger = setup_logger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["predictions"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Make a prediction",
    description="Endpoint to make predictions using the trained model",
)
async def predict(
    data: PredictRequest,
) -> Dict[str, Any]:
    """
    Make a prediction using the trained model.
    
    Args:
        data (PredictRequest): Input data for prediction
        
    Returns:
        JSONResponse: Prediction results
        
    Raises:
        HTTPException: If prediction fails or invalid input
    """
    try:
        logger.info(f"Received prediction request with data: {data}")
        
        # Input validation
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No input data provided"
            )
            
        # Make prediction
        prediction = await PredictService.run_model(data)
        
        logger.info(f"Successfully generated prediction: {prediction}")
        
        return JSONResponse(
            content={
                "status": "success",
                "prediction": prediction,
                "message": "Prediction generated successfully"
            },
            status_code=status.HTTP_200_OK
        )
        
    except ModelPredictionError as e:
        logger.error(f"Model prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model prediction failed: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
