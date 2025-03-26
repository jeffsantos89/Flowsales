import requests
import pytest
from unittest.mock import patch, Mock
import json

BASE_URL = "http://localhost:8000"

def test_auth_endpoint():
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": "test@example.com", "password": "123456"})
    assert response.status_code == 200

def test_prediction_endpoint():
    response = requests.post(f"{BASE_URL}/predict", json={"historical_sales": [10, 20, 30]})
    assert response.status_code == 200
    @pytest.fixture
    def mock_token():
        return "dummy_token"

    @pytest.fixture
    def auth_headers(mock_token):
        return {"Authorization": f"Bearer {mock_token}"}

    @pytest.mark.parametrize("test_input,expected", [
        ({"email": "test@example.com", "password": "123456"}, 200),
        ({"email": "invalid", "password": ""}, 400),
    ])
    def test_auth_endpoint_cases(test_input, expected):
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = expected
            mock_post.return_value = mock_response
            response = requests.post(f"{BASE_URL}/auth/login", json=test_input)
            assert response.status_code == expected

    @pytest.mark.parametrize("sales_data", [
        [10, 20, 30],
        [],
        [1000, 2000],
        [-1, 0, 1]
    ])
    def test_prediction_endpoint_variations(sales_data, auth_headers):
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"prediction": 100}
            mock_post.return_value = mock_response
            
            response = requests.post(
                f"{BASE_URL}/predict",
                json={"historical_sales": sales_data},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert "prediction" in response.json()

    def test_server_error_handling():
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError
            
            with pytest.raises(requests.exceptions.ConnectionError):
                requests.post(f"{BASE_URL}/predict", json={"historical_sales": [10]})