import os
import logging
from typing import Dict, Any

class FeatureFlags:
    ENABLE_ADVANCED_ANALYTICS = os.getenv("ENABLE_ADVANCED_ANALYTICS", "false").lower() == "true"
    ENABLE_QUANTUM_OPTIMIZATIONS = os.getenv("ENABLE_QUANTUM_OPTIMIZATIONS", "false").lower() == "true"
    ENABLE_REAL_TIME_REPORTING = os.getenv("ENABLE_REAL_TIME_REPORTING", "false").lower() == "true"

feature_flags = FeatureFlags()
logger = logging.getLogger(__name__)

class FeatureFlagManager:
    _instance = None
    _flags_cache: Dict[str, bool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getattr__(self, name: str) -> bool:
        if not hasattr(FeatureFlags, name):
            logger.warning(f"Attempted to access undefined feature flag: {name}")
            return False
        
        if name not in self._flags_cache:
            try:
                self._flags_cache[name] = getattr(FeatureFlags, name)
                logger.debug(f"Feature flag {name} = {self._flags_cache[name]}")
            except Exception as e:
                logger.error(f"Error accessing feature flag {name}: {str(e)}")
                return False
                
        return self._flags_cache[name]

    def refresh_cache(self) -> None:
        self._flags_cache.clear()
        logger.info("Feature flags cache cleared")

feature_manager = FeatureFlagManager()