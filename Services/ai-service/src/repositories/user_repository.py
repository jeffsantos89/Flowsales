from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
from repositories.base_repository import BaseRepository
import logging
from functools import lru_cache
from datetime import datetime
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)
        self.logger = logging.getLogger(__name__)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Retrieve user by email with error handling and logging.
        
        Args:
            db (Session): Database session
            email (str): User's email
            
        Returns:
            Optional[User]: User instance if found, None otherwise
        """
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                self.logger.info(f"User with email {email} not found")
                return None
            return user
        except SQLAlchemyError as e:
            self.logger.error(f"Database error while fetching user by email: {str(e)}")
            raise

    @lru_cache(maxsize=128)
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Cached retrieval of user by ID."""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error while fetching user by ID: {str(e)}")
            raise

    def get_active_users(self, db: Session) -> List[User]:
        """Retrieve all active users."""
        try:
            return db.query(User).filter(User.is_active == True).all()
        except SQLAlchemyError as e:
            self.logger.error("Database error while fetching active users")
            raise

    def update_last_login(self, db: Session, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            user = self.get_user_by_id(db, user_id)
            if user:
                user.last_login = datetime.utcnow()
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.logger.error(f"Error updating last login for user {user_id}")
            db.rollback()
            raise

    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Deactivate a user account."""
        try:
            user = self.get_user_by_id(db, user_id)
            if user:
                user.is_active = False
                user.deactivated_at = datetime.utcnow()
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.logger.error(f"Error deactivating user {user_id}")
            db.rollback()
            raise
