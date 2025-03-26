import logging
from typing import Any, Dict, List, Optional
from functools import lru_cache
from ml_models.model_registry import ModelRegistry
from quantum.optimizations.quantum_machine_learning import QuantumML
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PredictionResult:
    prediction: Any
    confidence: float
    model_version: str
    timestamp: str

class InferenceSystem:
    """
    A robust inference system that handles both classical ML and quantum predictions
    with error handling, caching, and logging capabilities.
    """
    
    def __init__(
        self,
        model_registry: Optional[ModelRegistry] = None,
        quantum_ml: Optional[QuantumML] = None,
        max_workers: int = 4
    ):
        self.logger = logging.getLogger(__name__)
        self.model_registry = model_registry or ModelRegistry()
        self.quantum_ml = quantum_ml or QuantumML()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    @lru_cache(maxsize=128)
    def predict_ml(self, data: Dict[str, Any]) -> PredictionResult:
        """
        Make ML predictions with caching and error handling.
        
        Args:
            data: Input data for prediction
            
        Returns:
            PredictionResult object containing prediction details
        """
        try:
            self.logger.info(f"Starting ML prediction with data: {data}")
            
            model = self.model_registry.load_model("ml_model_v1")
            prediction = model.predict([data])
            confidence = model.predict_proba([data]).max()
            
            result = PredictionResult(
                prediction=prediction[0],
                confidence=float(confidence),
                model_version=model.version,
                timestamp=datetime.now().isoformat()
            )
            
            self.logger.info(f"ML prediction completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in ML prediction: {str(e)}")
            raise InferenceError(f"ML prediction failed: {str(e)}")

    async def predict_quantum(self, params: Dict[str, Any]) -> PredictionResult:
        """
        Make quantum predictions asynchronously.
        
        Args:
            params: Quantum circuit parameters
            
        Returns:
            PredictionResult object containing prediction details
        """
        try:
            self.logger.info("Starting quantum prediction")
            
            # Run quantum computation in thread pool to avoid blocking
            quantum_circuit = await self.executor.submit(
                self.quantum_ml.build_model,
                **params
            )
            
            result = PredictionResult(
                prediction=quantum_circuit,
                confidence=self.quantum_ml.get_confidence(),
                model_version=self.quantum_ml.version,
                timestamp=datetime.now().isoformat()
            )
            
            self.logger.info(f"Quantum prediction completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in quantum prediction: {str(e)}")
            raise InferenceError(f"Quantum prediction failed: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown()

class InferenceError(Exception):
    """Custom exception for inference errors"""
    pass
