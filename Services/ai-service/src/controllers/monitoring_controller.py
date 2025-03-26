from fastapi import APIRouter
from services.monitoring_service import MonitoringService

router = APIRouter()

@router.get("/status")
async def system_status():
    status = MonitoringService.get_system_status()
    return {"status": status}
    @router.get("/ai-health")
    async def ai_health_check():
        health_metrics = MonitoringService.get_ai_health_metrics()
        return {"ai_status": health_metrics}

    @router.get("/resources")
    async def resource_usage():
        metrics = MonitoringService.get_resource_metrics()
        return {
            "cpu_usage": metrics.cpu,
            "memory_usage": metrics.memory,
            "gpu_usage": metrics.gpu,
            "storage": metrics.storage
        }

    @router.get("/alerts")
    async def get_alerts():
        alerts = MonitoringService.get_active_alerts()
        return {"alerts": alerts}

    @router.post("/alerts/threshold")
    async def set_alert_threshold(resource: str, value: float):
        MonitoringService.set_alert_threshold(resource, value)
        return {"message": "Alert threshold updated"}

    @router.get("/metrics/history")
    async def get_metrics_history(hours: int = 24):
        history = MonitoringService.get_metrics_history(hours)
        return {"metrics_history": history}