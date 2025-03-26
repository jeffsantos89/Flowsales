from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from database.db_session import get_db
from services.auth_service import get_current_user
from services.dashboard_service import DashboardService
from schemas.dashboard_schema import DashboardResponse
from typing import Optional
from datetime import datetime
import logging
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from core.exceptions import CustomException

# Configuração do logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/metrics",
    response_model=DashboardResponse,
    summary="Obtém métricas do dashboard",
    description="Endpoint para recuperar métricas e dados analíticos do dashboard",
    response_description="Retorna as métricas do dashboard"
)
@cache(expire=300)  # Cache de 5 minutos
async def get_dashboard_data(
    date_from: Optional[datetime] = Query(None, description="Data inicial para filtrar"),
    date_to: Optional[datetime] = Query(None, description="Data final para filtrar"),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
) -> DashboardResponse:
    """
    Recupera dados do dashboard com os seguintes recursos:
    - Filtragem por período
    - Cache de resultados
    - Logging detalhado
    - Tratamento de erros específicos
    """
    try:
        logger.info(f"Obtendo dados do dashboard para usuário {current_user.id}")
        
        dashboard_service = DashboardService(db)
        metrics = await dashboard_service.get_dashboard_metrics(
            user=current_user,
            date_from=date_from,
            date_to=date_to
        )
        
        logger.info("Dados do dashboard recuperados com sucesso")
        return metrics

    except CustomException as ce:
        logger.error(f"Erro customizado: {str(ce)}")
        raise HTTPException(
            status_code=ce.status_code,
            detail=ce.detail
        )
    
    except ValueError as ve:
        logger.error(f"Erro de validação: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validação: {str(ve)}"
        )
        
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao processar a requisição"
        )

@router.get("/health")
async def health_check():
    """Endpoint de health check para monitoramento"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "timestamp": datetime.utcnow()}
    )
