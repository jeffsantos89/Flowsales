import logging
from typing import List, Any, Optional
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from database import db_session

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryOptimizer:
    def __init__(self):
        self.last_optimization: Optional[datetime] = None
        
    @contextmanager
    def safe_session(self):
        """Gerenciador de contexto para sessões seguras do banco de dados"""
        session = db_session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()

    def optimize_query(self, force: bool = False) -> bool:
        """
        Otimiza o banco de dados com análise e vacuum.
        
        Args:
            force (bool): Força a otimização mesmo se já foi feita recentemente
            
        Returns:
            bool: True se a otimização foi bem-sucedida
        """
        # Evita otimizações muito frequentes
        if not force and self.last_optimization:
            time_diff = (datetime.now() - self.last_optimization).total_seconds()
            if time_diff < 3600:  # 1 hora
                logger.info("Skipping optimization - too soon since last run")
                return False

        try:
            with self.safe_session() as session:
                logger.info("Starting database optimization...")
                session.execute(text("ANALYZE;"))
                session.execute(text("VACUUM FULL;"))
                self.last_optimization = datetime.now()
                logger.info("Database optimization completed successfully")
                return True
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            return False

    def execute_fast_query(self, min_amount: float = 1000, limit: int = 50) -> List[Any]:
        """
        Executa uma consulta otimizada com parâmetros configuráveis.
        
        Args:
            min_amount (float): Valor mínimo para filtrar
            limit (int): Limite de resultados
            
        Returns:
            List[Any]: Resultados da consulta
        """
        try:
            with self.safe_session() as session:
                query = text("""
                    SELECT s.* 
                    FROM sales s 
                    WHERE s.amount > :min_amount 
                    ORDER BY s.amount DESC 
                    LIMIT :limit
                """)
                
                result = session.execute(
                    query,
                    {"min_amount": min_amount, "limit": limit}
                )
                return result.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return []

def main():
    try:
        optimizer = QueryOptimizer()
        
        # Tenta otimizar o banco de dados
        if optimizer.optimize_query():
            logger.info("Database optimization successful")
        
        # Executa a consulta otimizada
        results = optimizer.execute_fast_query(min_amount=1000, limit=50)
        logger.info(f"Query returned {len(results)} results")
        
        return results
        
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        return []

if __name__ == "__main__":
    results = main()
    print("🚀 Consulta rápida:", results)
