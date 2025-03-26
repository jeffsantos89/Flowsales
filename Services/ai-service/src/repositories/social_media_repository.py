from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, and_
import logging
from models.social_media_logs import SocialMediaLog
from repositories.base_repository import BaseRepository
from core.exceptions import DatabaseError, ValidationError
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

logger = logging.getLogger(__name__)

class SocialMediaRepository(BaseRepository[SocialMediaLog]):
    VALID_PLATFORMS = {'facebook', 'instagram', 'linkedin'}
    VALID_MESSAGE_TYPES = {'comment', 'direct_message', 'post', 'story'}
    
    def __init__(self):
        super().__init__(SocialMediaLog)
        
    def get_logs_by_platform(
        self, 
        db: Session, 
        platform: str, 
        limit: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[SocialMediaLog]:
        """
        Fetch interactions from a specific social media platform with filtering options.
        
        Args:
            db: Database session
            platform: Social media platform name
            limit: Maximum number of records to return
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of SocialMediaLog objects
        
        Raises:
            ValidationError: If platform is invalid
            DatabaseError: If database operation fails
        """
        try:
            self._validate_platform(platform)
            
            query = db.query(SocialMediaLog).filter(
                SocialMediaLog.platform == platform
            )
            
            if start_date:
                query = query.filter(SocialMediaLog.timestamp >= start_date)
            if end_date:
                query = query.filter(SocialMediaLog.timestamp <= end_date)
                
            return query.order_by(desc(SocialMediaLog.timestamp)).limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching logs: {str(e)}")
            raise DatabaseError(f"Failed to fetch logs for platform {platform}")

    def save_interaction(
        self, 
        db: Session, 
        user_id: int, 
        platform: str, 
        message: str, 
        message_type: str,
        metadata: dict = None
    ) -> SocialMediaLog:
        """
        Save a user interaction with additional validation and metadata support.
        
        Args:
            db: Database session
            user_id: ID of the user
            platform: Social media platform name
            message: Content of the interaction
            message_type: Type of interaction
            metadata: Optional additional data
            
        Returns:
            Created SocialMediaLog instance
            
        Raises:
            ValidationError: If input data is invalid
            DatabaseError: If database operation fails
        """
        try:
            self._validate_platform(platform)
            self._validate_message_type(message_type)
            self._validate_message(message)
            
            log_entry = SocialMediaLog(
                user_id=user_id,
                platform=platform,
                message=message,
                message_type=message_type,
                metadata=metadata,
                timestamp=datetime.utcnow()
            )
            
            return self.create(db, log_entry)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while saving interaction: {str(e)}")
            raise DatabaseError("Failed to save social media interaction")

    def _validate_platform(self, platform: str) -> None:
        if platform.lower() not in self.VALID_PLATFORMS:
            raise ValidationError(f"Invalid platform. Must be one of: {self.VALID_PLATFORMS}")

    def _validate_message_type(self, message_type: str) -> None:
        if message_type.lower() not in self.VALID_MESSAGE_TYPES:
            raise ValidationError(f"Invalid message type. Must be one of: {self.VALID_MESSAGE_TYPES}")

    def _validate_message(self, message: str) -> None:
        if not message or len(message) > 5000:  # Example limit
            raise ValidationError("Message must not be empty and cannot exceed 5000 characters")
