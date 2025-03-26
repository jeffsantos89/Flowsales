"""
Natural Language Processing (NLP) Package
---------------------------------------

This package provides semantic analysis and intent detection capabilities for Flowsale bots.
It includes the abstract base class `NLPProcessor` and its implementation `HuggingFaceProcessor`
with support for multiple models and automatic fallback mechanisms.

Features:
- Modular architecture for multiple NLP processors
- Type-safe implementations with robust error handling
- Automatic model fallback capabilities
- Comprehensive result analysis interfaces
- Production-ready logging and monitoring

Copyright (c) Flowsale. All rights reserved.
"""

from typing import List, Type

# Core components
from ai.nlp.base import (
    NLPProcessor,
    AnalysisResult,
    IntentConfidence,
    NLPProcessorException,
)

# Implementation specific
from ai.nlp.huggingface_processor import (
    HuggingFaceProcessor,
    PredictionResult,
    ModelType,
)

# Version control
__version__ = '1.0.0'
__author__ = 'Flowsale Team'

# Public API definition
__all__: List[str] = [
    # Base abstractions
    "NLPProcessor",
    "AnalysisResult",
    "IntentConfidence",
    "NLPProcessorException",
    
    # HuggingFace implementation
    "HuggingFaceProcessor",
    "PredictionResult", 
    "ModelType",
]

# Type verification
def verify_exports() -> None:
    """Verify that all exported items exist and are properly typed."""
    for item in __all__:
        assert item in globals(), f"Missing export: {item}"

# Run verification in debug mode
if __debug__:
    verify_exports()
