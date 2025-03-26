from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import logging
from pydantic import BaseModel, EmailStr
from database import get_db
from services.auth_service import AuthService
from schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse
from core.security import verify_password, create_access_token, get_current_user
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and return JWT token
    """
    try:
        user = await AuthService.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={"sub": user.username, "email": user.email}
        )
        refresh_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(days=7)
        )

        logger.info(f"User {user.username} successfully logged in")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        if await AuthService.get_user_by_email(db, request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        if await AuthService.get_user_by_username(db, request.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create new user
        user = await AuthService.create_user(db, request)
        logger.info(f"New user registered: {user.username}")
        return {"message": "User successfully registered"}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh-token")
async def refresh_token(
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    """
    try:
        current_user = await get_current_user(db, current_token)
        access_token = create_access_token(
            data={"sub": current_user.username, "email": current_user.email}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user and invalidate token
    """
    try:
        await AuthService.logout_user(db, current_user.id)
        logger.info(f"User {current_user.username} logged out")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
