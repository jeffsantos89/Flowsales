from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from models.recommendations import Recommendation
from schemas.recommendations import RecommendationResponse
import logging
from fastapi.responses import JSONResponse
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{user_id}", 
    response_model=List[RecommendationResponse],
    summary="Get user recommendations",
    description="Retrieve personalized recommendations for a specific user",
    response_description="List of recommendations for the user"
)
async def get_recommendations(
    user_id: int,
    limit: Optional[int] = Query(default=10, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    db: Session = Depends(get_db)
) -> List[RecommendationResponse]:
    """
    Get recommendations for a specific user with pagination support.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of recommendations to return
        offset: Number of recommendations to skip
        db: Database session
    
    Returns:
        List of recommendation objects
    
    Raises:
        HTTPException: If user not found or database error occurs
    """
    try:
        # Log the request
        logger.info(f"Fetching recommendations for user_id: {user_id} at {datetime.utcnow()}")
        
        # Check if user exists (assuming you have a User model)
        # user = db.query(User).filter(User.id == user_id).first()
        # if not user:
        #     raise HTTPException(status_code=404, detail="User not found")
        
        # Get recommendations with pagination
        recommendations = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        if not recommendations:
            logger.info(f"No recommendations found for user_id: {user_id}")
            return []
        
        logger.info(f"Successfully retrieved {len(recommendations)} recommendations")
        return recommendations
        
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching recommendations"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        content={"status": "healthy", "timestamp": datetime.utcnow().isoformat()},
        status_code=200
    )
