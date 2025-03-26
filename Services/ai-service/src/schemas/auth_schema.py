from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator, constr
from enum import Enum
import re

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class PasswordStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$', v):
            raise ValueError('Password must contain uppercase, lowercase, number and special character')
        return v

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe"
            }
        }

class UserCreate(UserBase):
    password: PasswordStr = Field(..., description="User password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

class UserResponse(UserBase):
    id: str = Field(..., description="User unique identifier")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User account status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "role": "user",
                "status": "active",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "last_login": "2023-01-01T00:00:00Z"
            }
        }

class PasswordReset(BaseModel):
    email: EmailStr = Field(..., description="User email address")

class PasswordUpdate(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: PasswordStr = Field(..., description="New password")
    confirm_new_password: str = Field(..., description="New password confirmation")

    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v