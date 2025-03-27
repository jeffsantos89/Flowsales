from fastapi import APIRouter, HTTPException
from typing import Optional
from src.controllers import instagram_controller
from src.middleware.error_handler import error_handler
from middleware.ratelimiter import rate_limiter
from auth import auth_required
from logging import logger

# Criar router com prefixo e tags para melhor organização da API
router = APIRouter(
    prefix="/instagram",
    tags=["instagram"],
    responses={404: {"description": "Not found"}},
)

# Aplicar middlewares
@router.middleware("http")
async def add_middlewares(request, call_next):
    try:
        # Rate limiting para prevenir abusos
        await rate_limiter(request)
        # Autenticação
        await auth_required(request)
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return error_handler(e)

# Incluir rotas do controller com validação de estado
try:
    router.include_router(
        instagram_controller.router,
        prefix="",
        responses={
            500: {"description": "Internal server error"},
            429: {"description": "Too many requests"},
            401: {"description": "Unauthorized"}
        }
    )
except Exception as e:
    logger.critical(f"Failed to include Instagram routes: {str(e)}")
    raise HTTPException(status_code=500, detail="Failed to initialize Instagram routes")
