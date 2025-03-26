from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from repositories.marketplace_repository import MarketplaceRepository
from models.marketplace_logs import MarketplaceLog
from fastapi import HTTPException
import logging
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketplaceAction(Enum):
    INTERACTION = "interaction"
    RECOMMENDATION = "recommendation"
    ERROR = "error"
    WARNING = "warning"

class MarketplaceService:
    def __init__(self, repository: Optional[MarketplaceRepository] = None):
        self._repository = repository or MarketplaceRepository()
        
    async def save_marketplace_message(
        self, 
        db: Session, 
        user_id: int, 
        marketplace: str, 
        message: str, 
        action: MarketplaceAction,
        metadata: dict = None
    ) -> MarketplaceLog:
        """
        Registra uma nova interação ou recomendação no marketplace.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário
            marketplace: Nome do marketplace
            message: Mensagem da interação
            action: Tipo de ação (enum MarketplaceAction)
            metadata: Dados adicionais opcional
            
        Returns:
            MarketplaceLog: Registro criado
            
        Raises:
            HTTPException: Em caso de erro na operação
        """
        try:
            logger.info(f"Saving marketplace message for user {user_id} in {marketplace}")
            
            if not message.strip():
                raise ValueError("Message cannot be empty")
                
            log = await self._repository.save_interaction(
                db=db,
                user_id=user_id,
                marketplace=marketplace.lower(),
                message=message,
                action=action.value,
                metadata=metadata,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Successfully saved marketplace message (ID: {log.id})")
            return log
            
        except Exception as e:
            logger.error(f"Error saving marketplace message: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_recent_marketplace_logs(
        self,
        db: Session,
        marketplace: str,
        limit: int = 10,
        skip: int = 0,
        action: MarketplaceAction = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[MarketplaceLog]:
        """
        Obtém os últimos registros de interações no marketplace com filtros.
        
        Args:
            db: Sessão do banco de dados
            marketplace: Nome do marketplace
            limit: Quantidade máxima de registros
            skip: Quantidade de registros para pular
            action: Filtro por tipo de ação
            start_date: Data inicial para filtro
            end_date: Data final para filtro
            
        Returns:
            List[MarketplaceLog]: Lista de registros encontrados
        """
        try:
            logger.info(f"Fetching logs for marketplace: {marketplace}")
            
            if limit > 100:
                logger.warning(f"Requested limit {limit} exceeds maximum of 100")
                limit = 100
                
            logs = await self._repository.get_logs_by_marketplace(
                db=db,
                marketplace=marketplace.lower(),
                limit=limit,
                skip=skip,
                action=action.value if action else None,
                start_date=start_date,
                end_date=end_date
            )
            
            logger.info(f"Found {len(logs)} logs")
            return logs
            
        except Exception as e:
            logger.error(f"Error fetching marketplace logs: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Instância singleton do serviço
marketplace_service = MarketplaceService()
