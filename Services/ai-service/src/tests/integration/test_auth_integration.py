import pytest
import json
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app
from src.core.config import settings
from src.models.user import User
from src.database.connection import get_db
from sqlalchemy.orm import Session
from src.services.auth_service import AuthService
from src.schemas.auth import UserCreate, UserLogin

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Setup test database connection
    db = next(get_db())
    yield db
    # Cleanup after tests
    db.close()

@pytest.fixture(scope="function")
def clean_db(test_db: Session):
    # Clean the test database before each test
    test_db.query(User).delete()
    test_db.commit()
    return test_db

@pytest.fixture
def valid_user_data():
    return {
        "email": "test@example.com",
        "password": "Test123!@#",
        "full_name": "Test User"
    }

class TestAuthIntegration:
    def test_register_user_success(self, clean_db, valid_user_data):
        response = client.post(
            "/api/v1/auth/register",
            json=valid_user_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == valid_user_data["email"]
        assert data["full_name"] == valid_user_data["full_name"]
        assert "password" not in data

    def test_register_user_duplicate_email(self, clean_db, valid_user_data):
        # First registration
        client.post("/api/v1/auth/register", json=valid_user_data)
        
        # Attempt duplicate registration
        response = client.post(
            "/api/v1/auth/register",
            json=valid_user_data
        )
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    def test_login_success(self, clean_db, valid_user_data):
        # Register user first
        client.post("/api/v1/auth/register", json=valid_user_data)
        
        # Attempt login
        login_data = {
            "email": valid_user_data["email"],
            "password": valid_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, clean_db, valid_user_data):
        # Register user first
        client.post("/api/v1/auth/register", json=valid_user_data)
        
        # Attempt login with wrong password
        login_data = {
            "email": valid_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_protected_route_with_token(self, clean_db, valid_user_data):
        # Register and login to get token
        client.post("/api/v1/auth/register", json=valid_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": valid_user_data["email"],
                "password": valid_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Test protected endpoint
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == valid_user_data["email"]

    def test_protected_route_without_token(self):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_password_validation(self, clean_db):
        weak_password_data = {
            "email": "test@example.com",
            "password": "weak",
            "full_name": "Test User"
        }
        response = client.post(
            "/api/v1/auth/register",
            json=weak_password_data
        )
        assert response.status_code == 422
        assert "password" in response.json()["detail"].lower()

    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "invalid@",
        "@invalid.com",
        "invalid@invalid",
    ])
    def test_invalid_email_formats(self, clean_db, invalid_email):
        invalid_data = {
            "email": invalid_email,
            "password": "Test123!@#",
            "full_name": "Test User"
        }
        response = client.post(
            "/api/v1/auth/register",
            json=invalid_data
        )
        assert response.status_code == 422
        assert "email" in response.json()["detail"].lower()

    def test_token_expiration(self, clean_db, valid_user_data):
        # This test assumes your token expires in a configurable time
        # You might need to adjust the token expiration time in your settings
        client.post("/api/v1/auth/register", json=valid_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": valid_user_data["email"],
                "password": valid_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Verify token works
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # You might want to add a test for expired tokens if you can manipulate
        # token expiration time in your test environment