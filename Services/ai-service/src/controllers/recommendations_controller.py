from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from pydantic import BaseModel, constr
from services.recommendations_service import RecommendationsService
from logging import getLogger
from datetime import datetime
import traceback

# Configure logger
logger = getLogger(__name__)

# Create router with tags for swagger documentation
router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Not found"}}
)

# Request/Response models
class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Dict]
    timestamp: datetime
    request_id: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

@router.get(
    "/{user_id}",
    response_model=RecommendationResponse,
    responses={
        200: {"description": "Successful response"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_recommendations(
    user_id: constr(min_length=1, max_length=50),  # type: ignore
    limit: Optional[int] = 10,
    category: Optional[str] = None
) -> JSONResponse:
    """
    Get personalized recommendations for a specific user.
    
    Args:
        user_id: The unique identifier of the user
        limit: Maximum number of recommendations to return
        category: Optional category filter for recommendations
    
    Returns:
        JSONResponse containing recommendations and metadata
    """
    try:
        logger.info(f"Fetching recommendations for user_id: {user_id}")
        
        # Input validation
        if limit and (limit < 1 or limit > 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )

        # Get recommendations from service
        recommendations = await RecommendationsService.get_recommendations(
            user_id=user_id,
            limit=limit,
            category=category
        )
        
        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No recommendations found for user_id: {user_id}"
            )

        response = RecommendationResponse(
            user_id=user_id,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
            request_id=generate_request_id()
        )

        logger.info(f"Successfully generated {len(recommendations)} recommendations for user_id: {user_id}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.dict()
        )

    except HTTPException as he:
        logger.warning(f"HTTP error for user_id {user_id}: {str(he)}")
        raise he

    except Exception as e:
        logger.error(f"Unexpected error for user_id {user_id}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )

def generate_request_id() -> str:
    """Generate a unique request ID"""
    from uuid import uuid4
    return str(uuid4())
