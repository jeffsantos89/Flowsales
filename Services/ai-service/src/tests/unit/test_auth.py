import pytest
from services.auth_service import authenticate_user

def test_authenticate_user_valid():
    token = authenticate_user("test@example.com", "securepassword")
    assert token is not None

def test_authenticate_user_invalid():
    token = authenticate_user("invalid@example.com", "wrongpassword")
    assert token is None
    def test_authenticate_user_empty_credentials():
        with pytest.raises(ValueError):
            authenticate_user("", "")

    def test_authenticate_user_invalid_email_format():
        with pytest.raises(ValueError):
            authenticate_user("invalid-email", "password")

    def test_authenticate_user_password_complexity():
        with pytest.raises(ValueError):
            authenticate_user("test@example.com", "short")

    @pytest.fixture
    def mock_user_db():
        return {"test@example.com": {"password_hash": "hashed_password", "is_active": True}}

    def test_authenticate_user_locked_account(mock_user_db):
        mock_user_db["test@example.com"]["is_active"] = False
        token = authenticate_user("test@example.com", "securepassword")
        assert token is None

    def test_authenticate_user_rate_limiting():
        for _ in range(5):
            authenticate_user("test@example.com", "wrongpassword")
        with pytest.raises(Exception, match="Too many attempts"):
            authenticate_user("test@example.com", "securepassword")