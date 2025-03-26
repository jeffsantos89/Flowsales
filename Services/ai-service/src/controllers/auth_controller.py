from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any
from services.auth_service import AuthService
from schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse
from logging import logger
from rate_limiter import rate_limit
from validators import validate_email
from middlewares.error_handler import handle_exceptions

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login", 
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Invalid credentials"},
        429: {"description": "Too many requests"}
    }
)
@rate_limit(max_requests=5, window_seconds=60)
@handle_exceptions
async def login(request: LoginRequest) -> Dict[str, Any]:
    """
    Authenticate user and return access token
    """
    try:
        if not validate_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        token = await AuthService.authenticate(request.email, request.password)
        logger.info(f"Successful login for user: {request.email}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Login failed for user {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid request"},
        409: {"description": "User already exists"}
    }
)
@rate_limit(max_requests=3, window_seconds=60)
@handle_exceptions
async def register(request: RegisterRequest) -> Dict[str, Any]:
    """
    Register a new user
    """
    try:
        if not validate_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        user = await AuthService.register_user(request)
        logger.info(f"New user registered: {user.id}")
        
        return {
            "message": "User created successfully",
            "user_id": user.id,
            "status": "success"
        }
    
    except ValueError as ve:
        logger.warning(f"Registration validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
