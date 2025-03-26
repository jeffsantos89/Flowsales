# src/ai/metrics/collectors/db_collector.py

from typing import Dict, Optional, List, Generator
from datetime import datetime
import logging
from dataclasses import dataclass
from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.base import Connection

from monitoring import MetricCollector, MetricValue

logger = logging.getLogger(__name__)

@dataclass
class DBMetric:
    """Classe para definir métricas do banco de dados."""
    name: str
    query: str
    labels: Dict[str, str]
    unit: str

class DBCollector(MetricCollector):
    """
    Coletor de métricas de banco de dados PostgreSQL via SQLAlchemy Engine.
    Implementa coleta de múltiplas métricas com tratamento de erros e timeout.
    """

    # Queries predefinidas para coleta de métricas
    DEFAULT_METRICS = [
        DBMetric(
            name="db_active_connections",
            query="SELECT count(*)::float FROM pg_stat_activity WHERE state = 'active'",
            labels={"state": "active"},
            unit="connections"
        ),
        DBMetric(
            name="db_idle_connections",
            query="SELECT count(*)::float FROM pg_stat_activity WHERE state = 'idle'",
            labels={"state": "idle"},
            unit="connections"
        ),
        DBMetric(
            name="db_deadlocks",
            query="SELECT deadlocks::float FROM pg_stat_database WHERE datname = current_database()",
            labels={"type": "deadlock"},
            unit="count"
        )
    ]

    def __init__(
        self, 
        engine: Engine,
        timeout: int = 5,
        custom_metrics: Optional[List[DBMetric]] = None
    ):
        """
        Inicializa o coletor de métricas.

        Args:
            engine: SQLAlchemy Engine configurada
            timeout: Timeout em segundos para queries
            custom_metrics: Lista opcional de métricas customizadas
        """
        self.engine = engine
        self.timeout = timeout
        self.metrics = custom_metrics or self.DEFAULT_METRICS

    @contextmanager
    def _get_connection(self) -> Generator[Connection, None, None]:
        """Gerencia conexão com o banco de dados com timeout."""
        conn = self.engine.connect()
        try:
            conn = conn.execution_options(timeout=self.timeout)
            yield conn
        finally:
            conn.close()

    def _collect_metric(self, conn: Connection, metric: DBMetric) -> Optional[MetricValue]:
        """Coleta uma métrica específica do banco de dados."""
        try:
            result = conn.execute(text(metric.query))
            value = result.scalar()
            
            if value is None:
                logger.warning(f"Métrica {metric.name} retornou None")
                return None

            return MetricValue(
                value=float(value),
                timestamp=datetime.utcnow(),
                labels=metric.labels,
                unit=metric.unit
            )
        except SQLAlchemyError as e:
            logger.error(f"Erro ao coletar métrica {metric.name}: {str(e)}")
            return None

    def collect(self) -> Dict[str, MetricValue]:
        """
        Coleta todas as métricas configuradas.
        
        Returns:
            Dict[str, MetricValue]: Dicionário com métricas coletadas
        
        Raises:
            SQLAlchemyError: Se houver erro na conexão com o banco
        """
        metrics = {}
        
        try:
            with self._get_connection() as conn:
                for metric in self.metrics:
                    result = self._collect_metric(conn, metric)
                    if result:
                        metrics[metric.name] = result
                        
            if not metrics:
                logger.warning("Nenhuma métrica foi coletada")
                
            return metrics

        except SQLAlchemyError as e:
            logger.exception("Erro crítico ao coletar métricas do banco de dados")
            raise

    def add_metric(self, metric: DBMetric) -> None:
        """Adiciona uma nova métrica para coleta."""
        if any(m.name == metric.name for m in self.metrics):
            raise ValueError(f"Métrica {metric.name} já existe")
        self.metrics.append(metric)

