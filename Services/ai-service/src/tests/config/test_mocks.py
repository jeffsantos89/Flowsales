import pytest
from unittest.mock import Mock, patch
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MockConfig:
    """Base configuration for mocks used in tests"""
    enabled: bool = True
    environment: str = "test"
    timestamp: datetime = datetime.now()

class MockFactory:
    """Factory class for creating standardized mock objects"""
    
    @staticmethod
    def create_response_mock(status_code: int = 200, 
                           data: Optional[Dict[str, Any]] = None, 
                           headers: Optional[Dict[str, str]] = None) -> Mock:
        """Creates a mock response object with standard attributes"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = data or {}
        mock_response.headers = headers or {"Content-Type": "application/json"}
        return mock_response

    @staticmethod
    def create_ai_service_mock() -> Mock:
        """Creates a mock for AI service interactions"""
        mock_service = Mock()
        mock_service.process.return_value = {
            "success": True,
            "prediction": "mock_prediction",
            "confidence": 0.95
        }
        return mock_service

@pytest.fixture
def mock_config() -> MockConfig:
    """Fixture for basic mock configuration"""
    return MockConfig()

@pytest.fixture
def mock_response():
    """Fixture for HTTP response mocks"""
    return MockFactory.create_response_mock()

@pytest.fixture
def mock_ai_service():
    """Fixture for AI service mocks"""
    return MockFactory.create_ai_service_mock()

@pytest.fixture
def mock_database():
    """Fixture for database interactions"""
    with patch('src.database.Database') as mock_db:
        mock_db.connect.return_value = True
        mock_db.query.return_value = []
        mock_db.insert.return_value = {"id": "mock-id"}
        yield mock_db

class TestContextManager:
    """Context manager for handling test environments"""
    
    def __init__(self, config: MockConfig):
        self.config = config
        self.original_state = {}

    def __enter__(self):
        # Save original state and setup test environment
        self.original_state = self._capture_current_state()
        self._setup_test_environment()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original state
        self._restore_state()

    def _capture_current_state(self) -> Dict[str, Any]:
        # Implementation for capturing current state
        return {}

    def _setup_test_environment(self):
        # Implementation for setting up test environment
        pass

    def _restore_state(self):
        # Implementation for restoring original state
        pass

# Constants for commonly used mock data
MOCK_DATA = {
    "user": {
        "id": "mock-user-id",
        "name": "Test User",
        "email": "test@example.com"
    },
    "product": {
        "id": "mock-product-id",
        "name": "Test Product",
        "price": 99.99
    }
}

def get_mock_data(key: str) -> Dict[str, Any]:
    """Helper function to retrieve standardized mock data"""
    return MOCK_DATA.get(key, {})