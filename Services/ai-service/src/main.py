# src/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_client import make_asgi_app
import asyncio
from typing import Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime

# Internal imports
from routes import api_router
from core.config import Settings
from core.logging_config import setup_logging
from core.middleware import (
    RequestValidatorMiddleware,
    RateLimiterMiddleware,
    AuthenticationMiddleware,
    ResponseTimeMiddleware,
    CompressionMiddleware
)
from core.security import setup_security
from core.monitoring import setup_metrics, setup_tracing
from core.database import init_db
from core.cache import Cache
from core.events import startup_handler, shutdown_handler
from utils.constants import API_PREFIX, API_TITLE, API_VERSION

class ApplicationState:
    """Global application state management"""
    def __init__(self):
        self.settings = Settings()
        self.cache = Cache()
        self.start_time = datetime.utcnow()
        self.is_healthy = True

class AIServiceAPI:
    def __init__(self):
        self.state = ApplicationState()
        self.logger = setup_logging()
        self.setup_sentry()
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await startup_handler(self.state)
            yield
            # Shutdown
            await shutdown_handler(self.state)

        self.app = FastAPI(
            title=API_TITLE,
            version=API_VERSION,
            docs_url=f"{API_PREFIX}/docs",
            redoc_url=f"{API_PREFIX}/redoc",
            openapi_url=f"{API_PREFIX}/openapi.json",
            lifespan=lifespan
        )
        
        self.setup_middleware()
        self.setup_routes()
        self.setup_exception_handlers()

    def setup_sentry(self):
        """Configure Sentry for error tracking"""
        sentry_sdk.init(
            dsn=self.state.settings.SENTRY_DSN,
            traces_sample_rate=1.0,
            environment=self.state.settings.ENVIRONMENT,
            integrations=[FastApiIntegration()],
            send_default_pii=False,
            attach_stacktrace=True,
            profiles_sample_rate=1.0,
        )

    def setup_middleware(self):
        """Configure application middleware stack"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.state.settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            allow_headers=["*"],
            max_age=600,
        )

        # Custom middleware stack
        self.app.add_middleware(CompressionMiddleware)
        self.app.add_middleware(ResponseTimeMiddleware)
        self.app.add_middleware(AuthenticationMiddleware)
        self.app.add_middleware(RateLimiterMiddleware)
        self.app.add_middleware(RequestValidatorMiddleware)

        # Security and monitoring
        setup_security(self.app)
        setup_metrics(self.app)
        setup_tracing(self.app)

        # Prometheus metrics
        metrics_app = make_asgi_app()
        self.app.mount("/metrics", metrics_app)

    def setup_routes(self):
        """Configure API routes"""
        self.app.include_router(api_router, prefix=API_PREFIX)

        @self.app.get("/health")
        async def health_check() -> Dict[str, Any]:
            """Enhanced health check endpoint"""
            return {
                "status": "healthy" if self.state.is_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": (datetime.utcnow() - self.state.start_time).total_seconds(),
                "version": API_VERSION,
                "environment": self.state.settings.ENVIRONMENT
            }

    def setup_exception_handlers(self):
        """Configure global exception handlers"""
        @self.app.exception_handler(HTTPException)
        async def custom_http_exception_handler(request: Request, exc: HTTPException):
            self.logger.error(f"HTTP error occurred: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "type": "http_error",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            self.logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "type": "server_error",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

def create_app() -> FastAPI:
    """Application factory pattern"""
    return AIServiceAPI().app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Settings().HOST,
        port=Settings().PORT,
        reload=Settings().DEBUG,
        workers=Settings().WORKERS,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*",
        access_log=True,
        loop="uvloop",
        http="httptools",
    )
