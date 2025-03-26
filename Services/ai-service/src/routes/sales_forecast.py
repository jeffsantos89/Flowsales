from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from logging import getLogger
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from joblib import dump, load
import os

# Configure logging
logger = getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/sales-forecast", tags=["Sales Forecast"])

# Data models
class SalesData(BaseModel):
    date: datetime
    product_id: str
    quantity: float
    price: float
    region: str
    
class ForecastRequest(BaseModel):
    product_id: str
    region: str
    forecast_periods: int = 30
    
class ForecastResponse(BaseModel):
    product_id: str
    region: str
    forecasts: List[dict]
    confidence_interval: dict

# Cache for trained models
MODEL_CACHE = {}
MODEL_PATH = "models/sales_forecast"

# Ensure model directory exists
os.makedirs(MODEL_PATH, exist_ok=True)

async def get_model(product_id: str, region: str):
    """Get or train model for specific product and region"""
    model_key = f"{product_id}_{region}"
    
    try:
        if model_key in MODEL_CACHE:
            return MODEL_CACHE[model_key]
            
        model_file = f"{MODEL_PATH}/{model_key}.joblib"
        if os.path.exists(model_file):
            MODEL_CACHE[model_key] = load(model_file)
            return MODEL_CACHE[model_key]
            
        return None
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise HTTPException(status_code=500, detail="Model loading error")

@router.post("/train")
async def train_model(sales_data: List[SalesData]):
    """Train forecasting model with historical sales data"""
    try:
        # Convert to DataFrame
        df = pd.DataFrame([s.dict() for s in sales_data])
        
        # Feature engineering
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # Group by product and region
        for (product_id, region), group in df.groupby(['product_id', 'region']):
            X = group[['year', 'month', 'day', 'day_of_week']]
            y = group['quantity']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Save model
            model_key = f"{product_id}_{region}"
            MODEL_CACHE[model_key] = model
            dump(model, f"{MODEL_PATH}/{model_key}.joblib")
            
        return JSONResponse(
            content={"message": "Models trained successfully"},
            status_code=200
        )
            
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail="Model training failed")

@router.post("/predict")
async def predict_sales(request: ForecastRequest):
    """Generate sales forecast"""
    try:
        model = await get_model(request.product_id, request.region)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found. Please train first.")
        
        # Generate future dates
        today = datetime.now()
        future_dates = pd.date_range(start=today, periods=request.forecast_periods)
        
        # Prepare features
        X_future = pd.DataFrame({
            'year': future_dates.year,
            'month': future_dates.month,
            'day': future_dates.day,
            'day_of_week': future_dates.dayofweek
        })
        
        # Generate predictions
        predictions = model.predict(X_future)
        
        # Calculate confidence intervals (using standard deviation of predictions)
        std_dev = np.std(predictions)
        lower_bound = predictions - (1.96 * std_dev)
        upper_bound = predictions + (1.96 * std_dev)
        
        # Prepare response
        forecasts = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "predicted_sales": float(pred)
            }
            for date, pred in zip(future_dates, predictions)
        ]
        
        confidence_interval = {
            "lower_bound": float(lower_bound.mean()),
            "upper_bound": float(upper_bound.mean()),
            "confidence_level": 0.95
        }
        
        return ForecastResponse(
            product_id=request.product_id,
            region=request.region,
            forecasts=forecasts,
            confidence_interval=confidence_interval
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@router.get("/model-status")
async def get_model_status():
    """Get status of trained models"""
    try:
        models = [f.replace('.joblib', '') for f in os.listdir(MODEL_PATH) if f.endswith('.joblib')]
        return {
            "total_models": len(models),
            "trained_models": models
        }
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Status check failed")