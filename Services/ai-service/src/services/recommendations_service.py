from repositories.recommendations_repository import get_top_recommendations
from typing import List, Dict, Optional
from fastapi import HTTPException
import logging
from datetime import datetime

def get_recommendations(user_id: str):
    return get_top_recommendations(user_id)
    logger = logging.getLogger(__name__)

    class RecommendationService:
        def __init__(self):
            self.cache = {}
            self.cache_timeout = 3600  # 1 hour

        async def get_recommendations(self, user_id: str, limit: int = 10) -> List[Dict]:
            try:
                if self._is_cached(user_id):
                    return self.cache[user_id]['data']

                recommendations = await get_top_recommendations(user_id, limit)
                self._cache_results(user_id, recommendations)
                
                if not recommendations:
                    logger.warning(f"No recommendations found for user {user_id}")
                    return []

                return recommendations

            except Exception as e:
                logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to get recommendations")

        def _is_cached(self, user_id: str) -> bool:
            if user_id in self.cache:
                cached_time = self.cache[user_id]['timestamp']
                if (datetime.now() - cached_time).seconds < self.cache_timeout:
                    return True
            return False

        def _cache_results(self, user_id: str, data: List[Dict]) -> None:
            self.cache[user_id] = {
                'data': data,
                'timestamp': datetime.now()
            }