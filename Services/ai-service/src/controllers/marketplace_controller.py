from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, constr
from typing import Dict, Optional
from enum import Enum
from datetime import datetime
from services.marketplace_service import MarketplaceService
from utils.logger import Logger
from middleware.auth import verify_api_key
from middleware.rate_limiter import rate_limit

# Define plataformas suportadas
class MarketplacePlatform(str, Enum):
    AMAZON = "amazon"
    SHOPEE = "shopee"
    MERCADO_LIVRE = "mercado_livre"

# Modelo de dados para a requisição
class ChatRequest(BaseModel):
    platform: MarketplacePlatform
    user_id: constr(min_length=1, max_length=100)
    message: constr(min_length=1, max_length=2000)
    order_id: Optional[str] = None
    context: Optional[Dict] = None

# Modelo de dados para a resposta
class ChatResponse(BaseModel):
    status: str
    message_id: str
    timestamp: datetime
    platform: str

router = APIRouter(prefix="/marketplace", tags=["marketplace"])
logger = Logger(__name__)

@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
@rate_limit(max_requests=100, window_seconds=60)
async def marketplace_chat(request: ChatRequest):
    try:
        # Log da requisição
        logger.info(f"Iniciando chat para plataforma: {request.platform}, user_id: {request.user_id}")

        # Validação específica por plataforma
        if request.platform == MarketplacePlatform.AMAZON:
            service = MarketplaceService.get_amazon_service()
        elif request.platform == MarketplacePlatform.SHOPEE:
            service = MarketplaceService.get_shopee_service()
        elif request.platform == MarketplacePlatform.MERCADO_LIVRE:
            service = MarketplaceService.get_mercadolivre_service()

        # Processa a mensagem
        response = await service.handle_chat(
            user_id=request.user_id,
            message=request.message,
            order_id=request.order_id,
            context=request.context
        )

        return ChatResponse(
            status="success",
            message_id=response.message_id,
            timestamp=datetime.utcnow(),
            platform=request.platform
        )

    except Exception as e:
        logger.error(f"Erro no processamento do chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no processamento da mensagem: {str(e)}"
        )

@router.get("/chat/{message_id}", response_model=Dict)
async def get_chat_status(message_id: str):
    try:
        return await MarketplaceService.get_chat_status(message_id)
    except Exception as e:
        logger.error(f"Erro ao buscar status do chat: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail="Mensagem não encontrada"
        )
