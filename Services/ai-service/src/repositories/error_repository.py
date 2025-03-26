from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, and_
import logging
from models.error_log import ErrorLog
from repositories.base_repository import BaseRepository
from fastapi import HTTPException
from repositories.repository_manager import repositories

async def obter_logs_usuario(db, user_id):
    return await repositories.whatsapp.get_logs_by_user(db, user_id=user_id)

logger = logging.getLogger(__name__)

class ErrorRepository(BaseRepository[ErrorLog]):
    """
    Repositório para gerenciamento de logs de erro no sistema.
    Fornece métodos para consulta, inserção e análise de erros.
    """

    def __init__(self):
        super().__init__(ErrorLog)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configura o logging para o repositório."""
        logging.basicConfig(level=logging.INFO)
    
    async def get_recent_errors(
        self, 
        db: Session, 
        limit: int = 10,
        skip: int = 0,
        error_type: Optional[str] = None
    ) -> List[ErrorLog]:
        """
        Retorna os erros mais recentes registrados no sistema.
        
        Args:
            db (Session): Sessão do banco de dados
            limit (int): Número máximo de registros
            skip (int): Número de registros para pular (paginação)
            error_type (str, optional): Filtrar por tipo de erro
            
        Returns:
            List[ErrorLog]: Lista de erros encontrados
            
        Raises:
            HTTPException: Se houver erro na consulta ao banco
        """
        try:
            query = db.query(ErrorLog)
            
            if error_type:
                query = query.filter(ErrorLog.error_type == error_type)
                
            return query.order_by(desc(ErrorLog.timestamp))\
                       .offset(skip)\
                       .limit(limit)\
                       .all()
                       
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar logs de erro: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao consultar banco de dados")

    async def get_errors_by_period(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> List[ErrorLog]:
        """Busca erros em um período específico."""
        try:
            return db.query(ErrorLog)\
                    .filter(and_(
                        ErrorLog.timestamp >= start_date,
                        ErrorLog.timestamp <= end_date
                    ))\
                    .order_by(desc(ErrorLog.timestamp))\
                    .all()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar logs por período: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao consultar banco de dados")

    async def get_error_statistics(
        self,
        db: Session,
        days: int = 7
    ) -> Dict[str, Any]:
        """Retorna estatísticas de erros dos últimos dias."""
        try:
            start_date = datetime.now() - timedelta(days=days)
            errors = db.query(ErrorLog)\
                      .filter(ErrorLog.timestamp >= start_date)\
                      .all()

            return {
                "total_errors": len(errors),
                "errors_by_type": self._count_errors_by_type(errors),
                "period_start": start_date,
                "period_end": datetime.now()
            }
        except SQLAlchemyError as e:
            logger.error(f"Erro ao gerar estatísticas: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao gerar estatísticas")

    def _count_errors_by_type(self, errors: List[ErrorLog]) -> Dict[str, int]:
        """Conta ocorrências de cada tipo de erro."""
        error_counts = {}
        for error in errors:
            error_counts[error.error_type] = error_counts.get(error.error_type, 0) + 1
        return error_counts
