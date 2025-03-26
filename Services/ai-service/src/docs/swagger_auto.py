from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from functools import lru_cache
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SwaggerConfig:
    def __init__(self):
        self.title = "Flowsale AI-Service"
        self.version = "1.0.0"
        self.description = "Documentação oficial do microserviço de IA e automações inteligentes da plataforma Flowsale"
        self.tags = [
            {"name": "Chatbots", "description": "Bots multicanal com IA"},
            {"name": "Analytics", "description": "Métricas e dashboards"},
            {"name": "Quantum", "description": "Algoritmos quânticos para previsão"},
            {"name": "Marketplace", "description": "Integrações com ML/Shopee"},
            {"name": "Segurança", "description": "Proteções, autenticação, limites"},
        ]
        self.contact = {
            "name": "Flowsale Support",
            "url": "https://flowsale.com.br/support",
            "email": "support@flowsale.com.br"
        }
        self.license_info = {
            "name": "Proprietary",
            "url": "https://flowsale.com.br/terms"
        }

@lru_cache(maxsize=1)
def get_cached_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """Cache the OpenAPI schema to improve performance"""
    config = SwaggerConfig()
    try:
        return get_openapi(
            title=config.title,
            version=config.version,
            description=config.description,
            routes=app.routes,
            tags=config.tags,
            contact=config.contact,
            license_info=config.license_info,
        )
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI schema: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate API documentation")

def setup_swagger(app: FastAPI):
    """Configure Swagger documentation endpoints with error handling and monitoring"""
    
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        try:
            logger.info("Serving Swagger UI documentation")
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=f"{SwaggerConfig().title} Docs",
                swagger_favicon_url="https://flowsale.com.br/favicon.png",
                swagger_ui_parameters={
                    "docExpansion": "none",
                    "defaultModelsExpandDepth": -1,
                    "syntaxHighlight.theme": "monokai"
                }
            )
        except Exception as e:
            logger.error(f"Failed to serve Swagger UI: {str(e)}")
            raise HTTPException(status_code=500, detail="Documentation temporarily unavailable")

    @app.get("/openapi.json", include_in_schema=False)
    async def openapi_spec():
        try:
            logger.info("Serving OpenAPI specification")
            schema = get_cached_openapi_schema(app)
            schema["info"]["x-generated-at"] = datetime.utcnow().isoformat()
            return JSONResponse(schema)
        except Exception as e:
            logger.error(f"Failed to serve OpenAPI spec: {str(e)}")
            raise HTTPException(status_code=500, detail="API specification temporarily unavailable")

