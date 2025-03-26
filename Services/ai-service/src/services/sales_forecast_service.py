from ai.ml_models.predict import forecast_sales
from repositories.sales_repository import get_historical_sales_data
import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException

def forecast_next_period(user_id: str):
    sales_data = get_historical_sales_data(user_id)
    return forecast_sales(sales_data)
    logger = logging.getLogger(__name__)

    class SalesForecastService:
        def __init__(self):
            self.logger = logging.getLogger(__name__)

        async def forecast_next_period(self, user_id: str, 
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Dict:
            try:
                if not user_id:
                    raise ValueError("User ID is required")
                
                self.logger.info(f"Fetching sales forecast for user {user_id}")
                sales_data = await get_historical_sales_data(user_id, start_date, end_date)
                
                if not sales_data or len(sales_data) < 30:
                    raise ValueError("Insufficient historical data for forecast")
                
                forecast_result = await forecast_sales(
                    sales_data=sales_data,
                    confidence_interval=0.95
                )
                
                return {
                    "user_id": user_id,
                    "forecast": forecast_result,
                    "generated_at": datetime.utcnow().isoformat(),
                    "status": "success"
                }

            except ValueError as ve:
                self.logger.error(f"Validation error: {str(ve)}")
                raise HTTPException(status_code=400, detail=str(ve))
            except Exception as e:
                self.logger.error(f"Error generating forecast: {str(e)}")
                raise HTTPException(status_code=500, detail="Error generating forecast")