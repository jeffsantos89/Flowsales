import jwt
import os
import logging
from datetime import datetime, timedelta

class JWTManager:
    SECRET = os.getenv("JWT_SECRET", "supersecret")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

    @staticmethod
    def create_token(data, expires_in=3600):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        payload = {
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow(),
            "data": data
        }
        try:
            token = jwt.encode(payload, JWTManager.SECRET, algorithm=JWTManager.ALGORITHM)
            return token
        except Exception as e:
            logging.error(f"Error creating token: {e}")
            raise

    @staticmethod
    def verify_token(token):
        try:
            decoded = jwt.decode(token, JWTManager.SECRET, algorithms=[JWTManager.ALGORITHM])
            return decoded["data"]
        except jwt.ExpiredSignatureError:
            logging.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logging.warning("Invalid token")
            return None
        except Exception as e:
            logging.error(f"Error verifying token: {e}")
            return None

# Configure logging
logging.basicConfig(level=logging.INFO)

jwt_manager = JWTManager()
