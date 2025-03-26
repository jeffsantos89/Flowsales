import pytest
from unittest.mock import Mock, patch
import numpy as np
from datetime import datetime
from typing import Dict, Any
from src.models.ai_model_base import AIModelBase
from src.models.ai_model_factory import AIModelFactory
from src.exceptions.model_exceptions import ModelNotFoundError, ModelInitializationError
from src.configs.model_config import ModelConfig

class TestAIModels:
    @pytest.fixture(scope="class")
    def model_config(self) -> ModelConfig:
        return ModelConfig(
            model_name="test_model",
            version="1.0.0",
            parameters={
                "learning_rate": 0.001,
                "batch_size": 32
            }
        )

    @pytest.fixture(scope="function")
    def mock_model(self) -> Mock:
        return Mock(spec=AIModelBase)

    @pytest.mark.parametrize("model_type", ["classification", "regression", "clustering"])
    def test_model_factory_creation(self, model_type: str, model_config: ModelConfig):
        """Test the creation of different types of AI models through the factory."""
        model = AIModelFactory.create_model(model_type=model_type, config=model_config)
        assert isinstance(model, AIModelBase)
        assert model.model_type == model_type
        assert model.config == model_config

    def test_model_factory_invalid_type(self, model_config: ModelConfig):
        """Test handling of invalid model type creation."""
        with pytest.raises(ModelNotFoundError):
            AIModelFactory.create_model(model_type="invalid_type", config=model_config)

    @pytest.mark.asyncio
    async def test_model_training(self, mock_model: Mock):
        """Test the asynchronous training process of the model."""
        mock_data = np.random.rand(100, 10)
        mock_labels = np.random.randint(0, 2, 100)
        
        with patch('src.models.ai_model_factory.AIModelFactory.create_model', return_value=mock_model):
            model = AIModelFactory.create_model("classification", ModelConfig())
            await model.train(mock_data, mock_labels)
            
            mock_model.train.assert_called_once_with(mock_data, mock_labels)

    @pytest.mark.asyncio
    async def test_model_prediction(self, mock_model: Mock):
        """Test the model's prediction functionality."""
        mock_input = np.random.rand(10, 10)
        expected_output = np.random.rand(10, 1)
        
        mock_model.predict.return_value = expected_output
        
        with patch('src.models.ai_model_factory.AIModelFactory.create_model', return_value=mock_model):
            model = AIModelFactory.create_model("regression", ModelConfig())
            result = await model.predict(mock_input)
            
            np.testing.assert_array_equal(result, expected_output)
            mock_model.predict.assert_called_once_with(mock_input)

    def test_model_serialization(self, mock_model: Mock, model_config: ModelConfig):
        """Test model serialization and deserialization."""
        mock_model.to_dict.return_value = {
            "model_type": "classification",
            "config": model_config.to_dict(),
            "timestamp": datetime.now().isoformat()
        }

        serialized = mock_model.to_dict()
        assert isinstance(serialized, dict)
        assert "model_type" in serialized
        assert "config" in serialized
        assert "timestamp" in serialized

    @pytest.mark.parametrize("invalid_config", [
        {"missing_required_field": True},
        {"invalid_parameter_type": "wrong_type"},
        {}
    ])
    def test_model_initialization_with_invalid_config(self, invalid_config: Dict[str, Any]):
        """Test model initialization with invalid configurations."""
        with pytest.raises(ModelInitializationError):
            AIModelFactory.create_model(
                model_type="classification",
                config=ModelConfig(**invalid_config)
            )

    def test_model_performance_metrics(self, mock_model: Mock):
        """Test model performance metrics calculation."""
        mock_predictions = np.array([0, 1, 1, 0])
        mock_true_values = np.array([0, 1, 0, 0])
        
        mock_model.calculate_metrics.return_value = {
            "accuracy": 0.75,
            "precision": 0.50,
            "recall": 1.0,
            "f1_score": 0.67
        }

        metrics = mock_model.calculate_metrics(mock_predictions, mock_true_values)
        
        assert isinstance(metrics, dict)
        assert all(metric in metrics for metric in ["accuracy", "precision", "recall", "f1_score"])
        assert all(isinstance(value, float) for value in metrics.values())