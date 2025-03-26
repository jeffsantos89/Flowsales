from security.auth import create_access_token, verify_password
from repositories.user_repository import get_user_by_email

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return create_access_token({"sub": user.email, "role": user.role})
    def authenticate_user_v2(email: str, password: str) -> dict:
        try:
            if not email or not password:
                raise ValueError("Email and password are required")
                
            user = get_user_by_email(email)
            if not user:
                raise ValueError("User not found")
                
            if not verify_password(password, user.hashed_password):
                raise ValueError("Invalid password")

            if not user.is_active:
                raise ValueError("User account is disabled")

            token_data = {
                "sub": user.email,
                "role": user.role,
                "user_id": str(user.id),
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            return {
                "access_token": create_access_token(token_data),
                "token_type": "bearer",
                "expires_in": 86400  # 24 hours in seconds
            }
            
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(str(e))
            class AuthenticationError(Exception):
                pass

            class AuthService:
                def __init__(self, logger=None):
                    self.logger = logger or logging.getLogger(__name__)

                def authenticate_user_v3(self, email: str, password: str) -> dict:
                    try:
                        self._validate_input(email, password)
                        user = self._get_and_validate_user(email, password)
                        return self._generate_token_response(user)
                    except Exception as e:
                        self.logger.error(f"Authentication error: {str(e)}", exc_info=True)
                        raise AuthenticationError(str(e))

                def _validate_input(self, email: str, password: str) -> None:
                    if not email or not isinstance(email, str):
                        raise ValueError("Invalid email format")
                    if not password or len(password) < 8:
                        raise ValueError("Password must be at least 8 characters")

                def _get_and_validate_user(self, email: str, password: str) -> Any:
                    user = get_user_by_email(email)
                    if not user:
                        self.logger.warning(f"Login attempt with non-existent email: {email}")
                        raise AuthenticationError("Invalid credentials")
                    
                    if not user.is_active:
                        self.logger.info(f"Login attempt for inactive user: {email}")
                        raise AuthenticationError("Account is disabled")
                        
                    if not verify_password(password, user.hashed_password):
                        self.logger.warning(f"Failed login attempt for user: {email}")
                        raise AuthenticationError("Invalid credentials")
                        
                    return user

                def _generate_token_response(self, user: Any) -> dict:
                    token_data = {
                        "sub": user.email,
                        "role": user.role,
                        "user_id": str(user.id),
                        "exp": datetime.utcnow() + timedelta(hours=24),
                        "iat": datetime.utcnow(),
                        "iss": "flowsale-auth-service"
                    }
                    
                    return {
                        "access_token": create_access_token(token_data),
                        "token_type": "bearer",
                        "expires_in": 86400,
                        "user_info": {
                            "email": user.email,
                            "role": user.role,
                            "id": str(user.id)
                        }
                    }