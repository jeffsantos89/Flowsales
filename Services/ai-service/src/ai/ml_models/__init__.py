"""
Core module for ML Models orchestration and integration in the Flowsale platform.
Provides components for training, inference, evaluation, versioning, and data engineering.

This module follows the Single Responsibility Principle and provides type hints
for better IDE support and code maintenance.
"""

from typing import List, Type

# Core components
from data_pipeline import DataPipeline
from feature_engineering import FeatureEngineering
from model_evaluation import (
    ModelEvaluation,
    RegressionMetrics,
    ClassificationMetrics,
    MetricType
)
from model_registry import ModelRegistry
from train import ModelTrainer
from predict import SalesPredictor

# Version control
__version__ = '1.0.0'
__author__ = 'Flowsale Team'

# Type definitions for better code completion and validation
ModelTypes = Type[ModelTrainer | SalesPredictor]
MetricTypes = Type[RegressionMetrics | ClassificationMetrics]

# Component registry for dependency injection
REGISTERED_COMPONENTS: List[str] = [
    "DataPipeline",
    "FeatureEngineering",
    "ModelEvaluation",
    "RegressionMetrics",
    "ClassificationMetrics",
    "MetricType",
    "ModelRegistry",
    "ModelTrainer",
    "SalesPredictor"
]

__all__ = REGISTERED_COMPONENTS

# Validation to ensure all components are properly imported
for component in REGISTERED_COMPONENTS:
    if component not in globals():
        raise ImportError(f"Required component {component} is not properly imported")
