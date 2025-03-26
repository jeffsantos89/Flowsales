from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from repositories.social_media_repository import SocialMediaRepository
from models.social_media_logs import SocialMediaLog
from logging import getLogger
from enum import Enum

logger = getLogger(__name__)

class SocialPlatform(Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"

class MessageType(Enum):
    POST = "post"
    COMMENT = "comment"
    DIRECT_MESSAGE = "dm"
    STORY = "story"

class SocialMediaService:
    def __init__(self):
        self._repository = SocialMediaRepository()
        
    async def save_social_message(
        self, 
        db: Session, 
        user_id: int, 
        platform: SocialPlatform,
        message: str, 
        message_type: MessageType,
        metadata: Optional[dict] = None
    ) -> SocialMediaLog:
        """
        Registra uma nova interação nas redes sociais.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            platform: Plataforma de mídia social
            message: Conteúdo da mensagem
            message_type: Tipo da mensagem
            metadata: Dados adicionais opcionais
            
        Returns:
            SocialMediaLog: Registro da interação criada
            
        Raises:
            HTTPException: Se ocorrer algum erro durante o processo
        """
        try:
            if not message.strip():
                raise ValueError("Message cannot be empty")

            timestamp = datetime.utcnow()
            
            log = await self._repository.save_interaction(
                db=db,
                user_id=user_id,
                platform=platform.value,
                message=message,
                message_type=message_type.value,
                metadata=metadata,
                created_at=timestamp
            )
            
            logger.info(
                f"Social media interaction saved - User: {user_id}, Platform: {platform.value}"
            )
            return log
            
        except Exception as e:
            logger.error(f"Error saving social media interaction: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save social media interaction: {str(e)}"
            )

    async def get_recent_social_interactions(
        self, 
        db: Session, 
        platform: SocialPlatform,
        limit: int = 10,
        user_id: Optional[int] = None,
        message_type: Optional[MessageType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[SocialMediaLog]:
        """
        Obtém as últimas interações nas redes sociais com filtros avançados.
        
        Args:
            db: Sessão do banco de dados
            platform: Plataforma de mídia social
            limit: Número máximo de registros
            user_id: Filtro opcional por usuário
            message_type: Filtro opcional por tipo de mensagem
            start_date: Data inicial para filtro
            end_date: Data final para filtro
            
        Returns:
            List[SocialMediaLog]: Lista de interações encontradas
        """
        try:
            if limit < 1 or limit > 100:
                raise ValueError("Limit must be between 1 and 100")

            logs = await self._repository.get_logs_by_platform(
                db=db,
                platform=platform.value,
                limit=limit,
                user_id=user_id,
                message_type=message_type.value if message_type else None,
                start_date=start_date,
                end_date=end_date
            )
            
            logger.info(
                f"Retrieved {len(logs)} social media interactions for platform {platform.value}"
            )
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving social media interactions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve social media interactions: {str(e)}"
            )
