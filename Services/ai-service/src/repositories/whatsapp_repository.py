from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.whatsapp_logs import WhatsappLog
from repositories.base_repository import BaseRepository
from datetime import datetime, timedelta
import logging
from functools import lru_cache
from fastapi import HTTPException
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

logger = logging.getLogger(__name__)

class WhatsappRepository(BaseRepository[WhatsappLog]):
    """
    Repositório para gerenciar logs do WhatsApp com funcionalidades avançadas.
    Inclui cache, logging, e tratamento de erros.
    """

    def __init__(self, cache_expiration: int = 300):
        """
        Inicializa o repositório.
        Args:
            cache_expiration (int): Tempo de expiração do cache em segundos
        """
        super().__init__(WhatsappLog)
        self.cache_expiration = cache_expiration

    async def get_logs_by_user(
        self, 
        db: Session, 
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[WhatsappLog]:
        """
        Busca interações de um usuário no WhatsApp com filtros de data.
        
        Args:
            db (Session): Sessão do banco de dados
            user_id (int): ID do usuário
            start_date (datetime, optional): Data inicial do filtro
            end_date (datetime, optional): Data final do filtro
        
        Returns:
            List[WhatsappLog]: Lista de logs encontrados
            
        Raises:
            HTTPException: Quando ocorre erro no banco de dados
        """
        try:
            query = db.query(WhatsappLog).filter(WhatsappLog.user_id == user_id)
            
            if start_date:
                query = query.filter(WhatsappLog.timestamp >= start_date)
            if end_date:
                query = query.filter(WhatsappLog.timestamp <= end_date)

            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar logs do usuário {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao buscar logs do WhatsApp")

    @lru_cache(maxsize=128)
    async def get_recent_logs(
        self, 
        db: Session, 
        limit: int = 10,
        hours_ago: int = 24
    ) -> List[WhatsappLog]:
        """
        Retorna as últimas interações registradas no WhatsApp com cache.
        
        Args:
            db (Session): Sessão do banco de dados
            limit (int): Limite de registros a retornar
            hours_ago (int): Filtrar registros das últimas X horas
            
        Returns:
            List[WhatsappLog]: Lista de logs recentes
            
        Raises:
            HTTPException: Quando ocorre erro no banco de dados
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=hours_ago)
            
            return (
                db.query(WhatsappLog)
                .filter(WhatsappLog.timestamp >= time_threshold)
                .order_by(WhatsappLog.timestamp.desc())
                .limit(limit)
                .all()
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar logs recentes: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao buscar logs recentes")

    async def delete_old_logs(self, db: Session, days: int = 30) -> int:
        """
        Remove logs antigos do sistema.
        
        Args:
            db (Session): Sessão do banco de dados
            days (int): Dias para considerar um log como antigo
            
        Returns:
            int: Número de registros deletados
        """
        try:
            threshold_date = datetime.utcnow() - timedelta(days=days)
            deleted = (
                db.query(WhatsappLog)
                .filter(WhatsappLog.timestamp < threshold_date)
                .delete()
            )
            db.commit()
            return deleted
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erro ao deletar logs antigos: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao deletar logs antigos")
