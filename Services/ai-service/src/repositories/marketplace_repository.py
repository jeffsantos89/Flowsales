from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.marketplace_logs import MarketplaceLog
from repositories.base_repository import BaseRepository
import logging
from fastapi import HTTPException
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

class MarketplaceRepository(BaseRepository[MarketplaceLog]):
    """Repository for handling marketplace interactions and logs."""
    
    VALID_MARKETPLACES = {'amazon', 'shopee', 'mercado_livre'}
    MAX_MESSAGE_LENGTH = 1000
    
    def __init__(self):
        super().__init__(MarketplaceLog)
        self.logger = logging.getLogger(__name__)

    def get_logs_by_marketplace(
        self, 
        db: Session, 
        marketplace: str, 
        limit: int = 50,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MarketplaceLog]:
        """
        Retrieve marketplace logs with advanced filtering options.
        
        Args:
            db: Database session
            marketplace: Marketplace name
            limit: Maximum number of records to return
            offset: Number of records to skip
            start_date: Filter logs after this date
            end_date: Filter logs before this date
        """
        try:
            self._validate_marketplace(marketplace)
            self._validate_pagination(limit, offset)

            query = db.query(MarketplaceLog).filter(
                MarketplaceLog.marketplace == marketplace.lower()
            )

            if start_date:
                query = query.filter(MarketplaceLog.timestamp >= start_date)
            if end_date:
                query = query.filter(MarketplaceLog.timestamp <= end_date)

            return query.order_by(MarketplaceLog.timestamp.desc())\
                       .offset(offset)\
                       .limit(limit)\
                       .all()

        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_logs_by_marketplace: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error occurred")

    def save_interaction(
        self, 
        db: Session, 
        user_id: int, 
        marketplace: str, 
        message: str, 
        action: str
    ) -> MarketplaceLog:
        """
        Save marketplace interactions with validation.
        
        Args:
            db: Database session
            user_id: ID of the user
            marketplace: Marketplace name
            message: Interaction message
            action: Type of action performed
        """
        try:
            self._validate_marketplace(marketplace)
            self._validate_message(message)
            self._validate_user_id(user_id)

            log_entry = MarketplaceLog(
                user_id=user_id,
                marketplace=marketplace.lower(),
                message=message,
                action=action,
                timestamp=datetime.utcnow()
            )

            return self.create(db, log_entry)

        except SQLAlchemyError as e:
            self.logger.error(f"Database error in save_interaction: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save interaction")
        
    def _validate_marketplace(self, marketplace: str) -> None:
        """Validate marketplace name."""
        if marketplace.lower() not in self.VALID_MARKETPLACES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid marketplace. Must be one of: {', '.join(self.VALID_MARKETPLACES)}"
            )

    def _validate_message(self, message: str) -> None:
        """Validate message length."""
        if not message or len(message) > self.MAX_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Message must be between 1 and {self.MAX_MESSAGE_LENGTH} characters"
            )

    def _validate_pagination(self, limit: int, offset: int) -> None:
        """Validate pagination parameters."""
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        if offset < 0:
            raise HTTPException(status_code=400, detail="Offset must be non-negative")

    def _validate_user_id(self, user_id: int) -> None:
        """Validate user ID."""
        if user_id < 1:
            raise HTTPException(status_code=400, detail="Invalid user ID")
