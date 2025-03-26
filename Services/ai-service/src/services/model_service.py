import logging
from typing import Optional, Dict, Any, List
import asyncio
from abc import ABC, abstractmethod
import json
from datetime import datetime
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelServiceException(Exception):
    """Custom exception for ModelService errors"""
    pass

class ModelInterface(ABC):
    """Abstract base class for model implementations"""
    @abstractmethod
    async def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def train(self, training_data: List[Dict[str, Any]]) -> None:
        pass

class ModelService:
    """
    Production-ready service for managing ML models with features like:
    - Async operations
    - Error handling
    - Logging
    - Model versioning
    - Health checks
    - Metrics tracking
    """

    def __init__(
        self,
        model_interface: ModelInterface,
        cache_dir: str = "./model_cache",
        max_retries: int = 3,
        timeout: int = 30
    ):
        self.model = model_interface
        self.cache_dir = Path(cache_dir)
        self.max_retries = max_retries
        self.timeout = timeout
        self.health_status = True
        self.metrics = {
            "predictions": 0,
            "errors": 0,
            "last_training": None
        }
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ModelService initialized with cache dir: {cache_dir}")

    async def predict_with_retry(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute prediction with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                result = await asyncio.wait_for(
                    self.model.predict(input_data),
                    timeout=self.timeout
                )
                self.metrics["predictions"] += 1
                return {
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": self._get_model_version()
                }
            except asyncio.TimeoutError:
                logger.error(f"Prediction timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    self.health_status = False
                    raise ModelServiceException("Prediction timeout after max retries")
            except Exception as e:
                logger.error(f"Prediction error: {str(e)}\n{traceback.format_exc()}")
                self.metrics["errors"] += 1
                if attempt == self.max_retries - 1:
                    self.health_status = False
                    raise ModelServiceException(f"Prediction failed: {str(e)}")

    async def train_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train the model with new data"""
        try:
            await self.model.train(training_data)
            self.metrics["last_training"] = datetime.utcnow().isoformat()
            await self._save_model_state()
            return {
                "status": "success",
                "timestamp": self.metrics["last_training"],
                "version": self._get_model_version()
            }
        except Exception as e:
            logger.error(f"Training error: {str(e)}\n{traceback.format_exc()}")
            raise ModelServiceException(f"Training failed: {str(e)}")

    async def _save_model_state(self) -> None:
        """Save model state and metrics"""
        try:
            metrics_path = self.cache_dir / "metrics.json"
            with open(metrics_path, "w") as f:
                json.dump(self.metrics, f)
            logger.info("Model state saved successfully")
        except Exception as e:
            logger.error(f"Error saving model state: {str(e)}")

    def _get_model_version(self) -> str:
        """Get current model version"""
        return f"v{hash(str(self.metrics))[:8]}"

    def get_health_status(self) -> Dict[str, Any]:
        """Return service health status and metrics"""
        return {
            "healthy": self.health_status,
            "metrics": self.metrics,
            "version": self._get_model_version()
        }

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            await self._save_model_state()
            logger.info("ModelService cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")