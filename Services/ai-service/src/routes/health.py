from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Coroutine, Optional, List
from enum import Enum
import logging
import asyncio
from pydantic import BaseModel, Field
import uuid

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants with configuration
class HealthConfig:
    HEALTHCHECK_TIMEOUT: float = 5.0
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    CACHE_TTL: int = 60  # Cache health results for 60 seconds
    VERSION: str = "1.1.0"

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class ServiceStatus(BaseModel):
    service_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_alive: bool
    latency_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    consecutive_failures: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class HealthResponse(BaseModel):
    status: HealthStatus
    services: Dict[str, ServiceStatus]
    timestamp: datetime
    version: str = HealthConfig.VERSION
    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    uptime: float
    environment: str

class HealthCheck:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1", tags=["Health"])
        self.health_targets: Dict[str, Any] = {}
        self.cache: Dict[str, ServiceStatus] = {}
        self.cache_timestamp: datetime = datetime.utcnow()
        self.start_time: datetime = datetime.utcnow()
        self.environment: str = "production"
        self.setup_routes()

    def register_service(self, name: str, service: Any, metadata: Dict[str, Any] = None) -> None:
        """Register a service for health checking with optional metadata."""
        if name in self.health_targets:
            logger.warning(f"Service {name} already registered, overwriting")
        self.health_targets[name] = {
            "service": service,
            "metadata": metadata or {}
        }

    async def check_service_health(self, name: str, check_func: Callable[..., Coroutine]) -> ServiceStatus:
        """Check health of a single service with improved retry and caching mechanism."""
        # Check cache first
        if name in self.cache and (datetime.utcnow() - self.cache_timestamp).seconds < HealthConfig.CACHE_TTL:
            return self.cache[name]

        start_time = datetime.utcnow()
        error_message = None
        consecutive_failures = 0

        for attempt in range(HealthConfig.MAX_RETRIES):
            try:
                async with asyncio.timeout(HealthConfig.HEALTHCHECK_TIMEOUT):
                    is_alive = await check_func()
                    end_time = datetime.utcnow()
                    latency = (end_time - start_time).total_seconds() * 1000

                    status = ServiceStatus(
                        is_alive=is_alive,
                        latency_ms=latency,
                        last_check=end_time,
                        consecutive_failures=consecutive_failures,
                        metadata=self.health_targets[name]["metadata"]
                    )
                    self.cache[name] = status
                    return status

            except Exception as e:
                error_message = str(e)
                consecutive_failures += 1
                logger.error(f"[HealthCheck] {name} failed (attempt {attempt + 1}/{HealthConfig.MAX_RETRIES}): {error_message}")
                if attempt < HealthConfig.MAX_RETRIES - 1:
                    await asyncio.sleep(HealthConfig.RETRY_DELAY)

        failed_status = ServiceStatus(
            is_alive=False,
            latency_ms=-1,
            last_check=datetime.utcnow(),
            error_message=error_message,
            consecutive_failures=consecutive_failures,
            metadata=self.health_targets[name]["metadata"]
        )
        self.cache[name] = failed_status
        return failed_status

    def determine_overall_status(self, services: Dict[str, ServiceStatus]) -> HealthStatus:
        """Determine overall system health with weighted status calculation."""
        if not services:
            return HealthStatus.UNHEALTHY

        alive_services = sum(1 for service in services.values() if service.is_alive)
        total_services = len(services)

        if alive_services == total_services:
            return HealthStatus.HEALTHY
        elif alive_services == 0:
            return HealthStatus.UNHEALTHY
        else:
            health_ratio = alive_services / total_services
            return HealthStatus.DEGRADED if health_ratio >= 0.5 else HealthStatus.UNHEALTHY

    async def check_health(self) -> HealthResponse:
        """Check health of all registered services with parallel execution."""
        service_statuses = {}
        check_tasks = []

        for name, service_info in self.health_targets.items():
            service = service_info["service"]
            check_method = getattr(service, 'healthcheck', None) or getattr(service, 'ping', None)
            
            if check_method:
                check_tasks.append(
                    self.check_service_health(name, check_method)
                )
            else:
                logger.error(f"Service {name} has no health check method")
                service_statuses[name] = ServiceStatus(
                    is_alive=False,
                    latency_ms=-1,
                    last_check=datetime.utcnow(),
                    error_message="No health check method available",
                    metadata=service_info["metadata"]
                )

        if check_tasks:
            results = await asyncio.gather(*check_tasks, return_exceptions=True)
            
            for (name, _), status in zip(self.health_targets.items(), results):
                if isinstance(status, Exception):
                    service_statuses[name] = ServiceStatus(
                        is_alive=False,
                        latency_ms=-1,
                        last_check=datetime.utcnow(),
                        error_message=str(status),
                        metadata=self.health_targets[name]["metadata"]
                    )
                else:
                    service_statuses[name] = status

        overall_status = self.determine_overall_status(service_statuses)
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return HealthResponse(
            status=overall_status,
            services=service_statuses,
            timestamp=datetime.utcnow(),
            uptime=uptime,
            environment=self.environment
        )

    def setup_routes(self) -> None:
        """Setup FastAPI routes with comprehensive health checking."""
        @self.router.get(
            "/healthz",
            summary="Comprehensive Health Check",
            response_model=HealthResponse,
            responses={
                200: {"description": "Service Healthy"},
                503: {"description": "Service Unhealthy or Degraded"},
                500: {"description": "Internal Server Error"}
            }
        )
        async def healthz():
            try:
                response = await self.check_health()
                status_code = status.HTTP_200_OK if response.status == HealthStatus.HEALTHY else status.HTTP_503_SERVICE_UNAVAILABLE
                return JSONResponse(content=response.dict(), status_code=status_code)
            except Exception as e:
                logger.exception("Health check failed")
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

# Create singleton instance
health_check = HealthCheck()
