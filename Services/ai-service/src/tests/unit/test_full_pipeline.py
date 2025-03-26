import pytest
from typing import Dict, List
from datetime import datetime
from services.auth_service import authenticate_user
from services.predict_service import predict_sales
from services.recommendations_service import get_recommendations
from services.models import SalesPredictionRequest
from unittest.mock import patch

class TestFullPipeline:
    @pytest.fixture
    def valid_credentials(self) -> Dict[str, str]:
        return {
            "email": "user@test.com",
            "password": "securepassword"
        }

    @pytest.fixture
    def sales_data(self) -> SalesPredictionRequest:
        return {
            "historical_sales": [100, 200, 300],
            "trend_factor": 1.2,
            "timestamp": datetime.now().isoformat(),
            "store_id": "store123"
        }

    def test_authentication_success(self, valid_credentials):
        """Test successful user authentication"""
        user_token = authenticate_user(
            email=valid_credentials["email"],
            password=valid_credentials["password"]
        )
        assert user_token is not None
        assert isinstance(user_token, str)
        assert len(user_token) > 0

    def test_sales_prediction(self, sales_data):
        """Test sales prediction with valid data"""
        prediction = predict_sales(sales_data)
        assert prediction is not None
        assert isinstance(prediction, float)
        assert prediction > 0
        assert prediction < float('inf')

    @pytest.mark.parametrize("user_id", ["user123", "user456"])
    def test_recommendations(self, user_id: str):
        """Test recommendations retrieval for different users"""
        recommendations = get_recommendations(user_id)
        assert isinstance(recommendations, list)
        assert all(isinstance(item, dict) for item in recommendations)

    @pytest.mark.parametrize("invalid_data", [
        {"historical_sales": [], "trend_factor": 1.2},
        {"historical_sales": [100], "trend_factor": -1},
        {"historical_sales": None, "trend_factor": 1.2},
    ])
    def test_sales_prediction_invalid_data(self, invalid_data):
        """Test sales prediction with invalid data"""
        with pytest.raises(ValueError):
            predict_sales(invalid_data)

    @patch('services.auth_service.authenticate_user')
    def test_authentication_failure(self, mock_auth):
        """Test authentication failure scenarios"""
        mock_auth.return_value = None
        result = authenticate_user("invalid@test.com", "wrongpassword")
        assert result is None

