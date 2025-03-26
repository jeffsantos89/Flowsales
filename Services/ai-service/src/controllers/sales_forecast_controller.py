from fastapi import APIRouter
from services.sales_forecast_service import SalesForecastService

router = APIRouter()

@router.get("/sales-forecast")
async def get_sales_forecast():
    forecast = SalesForecastService.predict_sales()
    return {"sales_forecast": forecast}
    @router.get("/sales-forecast/{period}")
    async def get_sales_forecast_by_period(
        period: str,
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None
    ):
        try:
            forecast = SalesForecastService.predict_sales(
                period=period,
                category=category,
                start_date=start_date,
                end_date=end_date
            )
            return {
                "status": "success",
                "data": {
                    "sales_forecast": forecast,
                    "period": period,
                    "category": category,
                    "date_range": {"start": start_date, "end": end_date}
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "details": {"type": type(e).__name__}
            }