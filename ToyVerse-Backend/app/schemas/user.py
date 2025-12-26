
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class UserBase(BaseModel):

    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    profile_picture: Optional[str] = Field(None, description="URL to profile picture")

class UserCreate(UserBase):

    password: str = Field(..., min_length=6, max_length=100, description="User password")
    role: Optional[str] = Field(default="customer", description="User role (admin/customer)")

    @validator('password')
    def password_strength(cls, v):

        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

    @validator('role')
    def validate_role(cls, v):

        if v not in ['admin', 'customer']:
            raise ValueError('Role must be either admin or customer')
        return v

class UserLogin(BaseModel):

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")

class UserResponse(UserBase):

    id: int
    role: str
    created_at: datetime
    permissions: List[str] = Field(default_factory=list, description="User permissions")

    class Config:

        from_attributes = True

class UserUpdate(BaseModel):

    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)

class Token(BaseModel):

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user information")

class TokenData(BaseModel):

    username: Optional[str] = None
    role: Optional[str] = None
