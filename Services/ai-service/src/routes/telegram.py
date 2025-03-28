from fastapi import APIRouter
from typing import Final
from src.controllers import telegram_controller
from fastapi.exceptions import HTTPException
from fastapi import status

# Constantes
API_VERSION: Final[str] = "v1"
API_PREFIX: Final[str] = f"/api/{API_VERSION}"

# Criação do router com configurações
router = APIRouter(
    prefix=API_PREFIX,
    tags=["telegram"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

try:
    # Inclusão das rotas do controller
    router.include_router(
        telegram_controller.router,
        prefix="/telegram"
    )
except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to include telegram routes: {str(e)}"
    )

# Middleware para logging (opcional)
@router.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    return response

# Health check endpoint
@router.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}