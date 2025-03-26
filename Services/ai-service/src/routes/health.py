from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any, Callable, Coroutine, Optional
from enum import Enum
import logging
import asyncio
from pydantic import BaseModel

# Constants
HEALTHCHECK_TIMEOUT = 5.0  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds

# Configure logging
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class ServiceStatus(BaseModel):
    is_alive: bool
    latency_ms: float
    last_check: datetime
    error_message: Optional[str] = None

class HealthResponse(BaseModel):
    status: HealthStatus
    services: Dict[str, ServiceStatus]
    timestamp: datetime
    version: str = "1.0"

class HealthCheck:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1", tags=["Health"])
        self.health_targets: Dict[str, Any] = {}
        self.setup_routes()

    def register_service(self, name: str, service: Any) -> None:
        """Register a service for health checking."""
        if name in self.health_targets:
            logger.warning(f"Service {name} already registered, overwriting")
        self.health_targets[name] = service

    async def check_service_health(self, name: str, check_func: Callable[..., Coroutine]) -> ServiceStatus:
        """Check health of a single service with retry mechanism."""
        start_time = datetime.utcnow()
        error_message = None

        for attempt in range(MAX_RETRIES):
            try:
                async with asyncio.timeout(HEALTHCHECK_TIMEOUT):
                    is_alive = await check_func()
                    end_time = datetime.utcnow()
                    latency = (end_time - start_time).total_seconds() * 1000

                    return ServiceStatus(
                        is_alive=is_alive,
                        latency_ms=latency,
                        last_check=end_time
                    )
            except Exception as e:
                error_message = str(e)
                logger.warning(f"[HealthCheck] {name} failed (attempt {attempt + 1}/{MAX_RETRIES}): {error_message}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)

        return ServiceStatus(
            is_alive=False,
            latency_ms=-1,
            last_check=datetime.utcnow(),
            error_message=error_message
        )

    def determine_overall_status(self, services: Dict[str, ServiceStatus]) -> HealthStatus:
        """Determine overall system health based on service statuses."""
        if all(service.is_alive for service in services.values()):
            return HealthStatus.HEALTHY
        elif not any(service.is_alive for service in services.values()):
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED

    async def check_health(self) -> HealthResponse:
        """Check health of all registered services."""
        service_statuses = {}
        check_tasks = []

        for name, service in self.health_targets.items():
            if hasattr(service, 'healthcheck'):
                check_tasks.append(
                    self.check_service_health(name, service.healthcheck)
                )
            elif hasattr(service, 'ping'):
                check_tasks.append(
                    self.check_service_health(name, service.ping)
                )
            else:
                logger.error(f"Service {name} has no health check method")
                continue

        results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        for (name, _), status in zip(self.health_targets.items(), results):
            if isinstance(status, Exception):
                service_statuses[name] = ServiceStatus(
                    is_alive=False,
                    latency_ms=-1,
                    last_check=datetime.utcnow(),
                    error_message=str(status)
                )
            else:
                service_statuses[name] = status

        overall_status = self.determine_overall_status(service_statuses)
        
        return HealthResponse(
            status=overall_status,
            services=service_statuses,
            timestamp=datetime.utcnow()
        )

    def setup_routes(self) -> None:
        """Setup FastAPI routes."""
        @self.router.get(
            "/healthz",
            summary="AI Service Health Check",
            response_model=HealthResponse,
            response_class=JSONResponse,
            responses={
                503: {"description": "Service Unhealthy or Degraded"},
                200: {"description": "Service Healthy"}
            }
        )
        async def healthz():
            response = await self.check_health()
            status_code = status.HTTP_200_OK if response.status == HealthStatus.HEALTHY else status.HTTP_503_SERVICE_UNAVAILABLE
            return JSONResponse(content=response.dict(), status_code=status_code)

# Usage
health_check = HealthCheck()
