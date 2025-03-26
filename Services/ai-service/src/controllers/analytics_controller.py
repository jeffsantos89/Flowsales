from fastapi import APIRouter
from services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/analytics")
async def get_analytics():
    analytics_data = AnalyticsService.get_model_performance()
    return {"analytics": analytics_data}
    @router.get("/analytics/detailed")
    async def get_detailed_analytics():
        """Get detailed AI model performance metrics and impact analysis."""
        try:
            performance_metrics = AnalyticsService.get_detailed_metrics()
            impact_analysis = AnalyticsService.get_business_impact()
            model_health = AnalyticsService.get_model_health_status()
            
            return {
                "performance_metrics": performance_metrics,
                "impact_analysis": impact_analysis,
                "model_health": model_health,
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    @router.get("/analytics/trends")
    async def get_analytics_trends():
        """Get historical performance trends and predictions."""
        try:
            historical_data = AnalyticsService.get_historical_performance()
            predictions = AnalyticsService.get_performance_predictions()
            
            return {
                "historical_trends": historical_data,
                "future_predictions": predictions,
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }