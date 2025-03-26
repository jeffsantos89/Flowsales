from analytics.analytics_engine import process_user_data
import logging
from functools import lru_cache
from typing import Dict, Optional
from time import time
from dataclasses import dataclass
from datetime import datetime

def generate_customer_insights(user_id):
    return process_user_data(user_id)
    @dataclass
    class CustomerInsight:
        user_id: str
        insights: Dict
        generated_at: datetime
        processing_time: float

    @lru_cache(maxsize=1000)
    def generate_customer_insights(user_id: str) -> Optional[CustomerInsight]:
        try:
            if not isinstance(user_id, str) or not user_id.strip():
                raise ValueError("Invalid user_id")
                
            logging.info(f"Generating insights for user: {user_id}")
            start_time = time()
            
            insights = process_user_data(user_id)
            
            result = CustomerInsight(
                user_id=user_id,
                insights=insights,
                generated_at=datetime.now(),
                processing_time=time() - start_time
            )
            
            logging.info(f"Successfully generated insights for user {user_id}")
            return result
            
        except Exception as e:
            logging.error(f"Error generating insights for user {user_id}: {str(e)}")
            raise