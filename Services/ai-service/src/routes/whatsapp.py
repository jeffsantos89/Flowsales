from fastapi import APIRouter, FastAPI
from typing import Optional
from src.controllers import whatsapp_controller
from src.middleware.error_handler import error_handler
from logging import logging_middleware
from src.config.settings import Settings

class WhatsAppRouter:
    def __init__(self, app: Optional[FastAPI] = None):
        self.router = APIRouter(
            prefix="/whatsapp",
            tags=["WhatsApp"],
            responses={404: {"description": "Not found"}},
        )
        
        # Configurações
        self.settings = Settings()
        
        # Middleware
        self.router.middleware("http")(logging_middleware)
        
        # Tratamento de erros
        self.router.exception_handler(Exception)(error_handler)
        
        # Inclusão das rotas do controller
        self.router.include_router(whatsapp_controller.router)
        
        # Registro no app principal se fornecido
        if app:
            app.include_router(self.router)

    def get_router(self) -> APIRouter:
        return self.router

# Instância para uso
whatsapp_routes = WhatsAppRouter()
router = whatsapp_routes.get_router()
