# src/ai/nlp/huggingface_processor.py

import logging
from typing import Optional, Dict, Any, List, Union, Tuple
from transformers import pipeline, Pipeline, AutoTokenizer, AutoModel
from ai.nlp.base import NLPProcessor
from functools import lru_cache
import torch
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelType(Enum):
    SENTIMENT = "sentiment"
    CLASSIFICATION = "classification"
    ZERO_SHOT = "zero-shot-classification"

@dataclass
class PredictionResult:
    label: str
    confidence: float
    processed_at: float
    processing_time: float

class HuggingFaceProcessor(NLPProcessor):
    """
    Advanced NLP processor using HuggingFace models with enhanced features.
    """
    
    DEFAULT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
    FALLBACK_MODEL = "bert-base-uncased"
    
    LABEL_MAPPING = {
        "positive": "comprar",
        "negative": "suporte",
        "neutral": "informacao",
        "default": "geral"
    }

    def __init__(
        self, 
        model_name: str = DEFAULT_MODEL,
        threshold: float = 0.5,
        cache_size: int = 1000,
        max_workers: int = 4,
        batch_size: int = 32,
        model_type: ModelType = ModelType.SENTIMENT,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Enhanced initialization with additional parameters.
        
        Args:
            model_name (str): Name of the model to use
            threshold (float): Confidence threshold for classification
            cache_size (int): Size of the LRU cache for results
            max_workers (int): Maximum number of worker threads
            batch_size (int): Batch size for processing
            model_type (ModelType): Type of model to use
            device (str): Device to use for computation
        """
        self.device = device
        self.batch_size = batch_size
        self.model_type = model_type
        self._initialize_components(model_name)
        self.threshold = threshold
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._setup_monitoring()

    def _initialize_components(self, model_name: str) -> None:
        """Initialize model components with fallback mechanism."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.classifier = self._load_pipeline(model_name)
            self._save_model_metadata(model_name)
        except Exception as e:
            logger.error(f"Failed to load primary model: {str(e)}")
            logger.info(f"Attempting to load fallback model: {self.FALLBACK_MODEL}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.FALLBACK_MODEL)
            self.classifier = self._load_pipeline(self.FALLBACK_MODEL)

    def _setup_monitoring(self) -> None:
        """Setup monitoring and metrics collection."""
        self.metrics = {
            "total_processed": 0,
            "cache_hits": 0,
            "average_processing_time": 0,
            "errors": 0
        }

    @staticmethod
    def _load_pipeline(model_name: str) -> Pipeline:
        """Load the HuggingFace pipeline with enhanced error handling."""
        try:
            return pipeline("text-classification", model=model_name, device=torch.cuda.current_device() if torch.cuda.is_available() else -1)
        except Exception as e:
            logger.critical(f"Critical error loading model pipeline: {str(e)}")
            raise RuntimeError(f"Failed to initialize model pipeline: {str(e)}")

    @lru_cache(maxsize=1000)
    def analyze(self, message: str) -> PredictionResult:
        """
        Enhanced message analysis with detailed results.
        
        Args:
            message (str): Input text to analyze
        
        Returns:
            PredictionResult: Structured prediction result
        """
        start_time = time.time()
        try:
            self.metrics["total_processed"] += 1
            
            if not message.strip():
                return self._create_default_result()

            result = self.classifier(message)[0]
            label = self.LABEL_MAPPING.get(result["label"], self.LABEL_MAPPING["default"])
            
            prediction = PredictionResult(
                label=label,
                confidence=result["score"],
                processed_at=time.time(),
                processing_time=time.time() - start_time
            )
            
            self._update_metrics(prediction)
            return prediction

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Error processing message: {str(e)}")
            return self._create_default_result()

    async def analyze_batch(self, messages: List[str]) -> List[PredictionResult]:
        """
        Batch processing of messages for better performance.
        """
        return await asyncio.gather(*[
            asyncio.to_thread(self.analyze, msg)
            for msg in messages
        ])

    def _create_default_result(self) -> PredictionResult:
        """Create a default result for error cases."""
        return PredictionResult(
            label=self.LABEL_MAPPING["default"],
            confidence=0.0,
            processed_at=time.time(),
            processing_time=0.0
        )

    def _update_metrics(self, prediction: PredictionResult) -> None:
        """Update processing metrics."""
        self.metrics["average_processing_time"] = (
            (self.metrics["average_processing_time"] * (self.metrics["total_processed"] - 1) +
             prediction.processing_time) / self.metrics["total_processed"]
        )

    def _save_model_metadata(self, model_name: str) -> None:
        """Save model metadata for monitoring."""
        metadata = {
            "model_name": model_name,
            "initialized_at": time.time(),
            "device": self.device,
            "model_type": self.model_type.value
        }
        Path("model_metadata.json").write_text(json.dumps(metadata))
