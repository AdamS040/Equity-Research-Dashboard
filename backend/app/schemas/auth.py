"""
Authentication related Pydantic schemas.

Contains schemas for user authentication, registration, and token management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class TokenData(BaseModel):
    """Token data schema."""
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """User update schema."""
    username: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""
    id: UUID
    username: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    role: str
    permissions: List[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    last_activity: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """User profile schema with additional fields."""
    full_name: str
    is_admin: bool
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str
    remember_me: bool = False


class UserRegister(UserCreate):
    """User registration schema."""
    agree_to_terms: bool = Field(..., description="Must agree to terms and conditions")
    
    @validator('agree_to_terms')
    def must_agree_to_terms(cls, v):
        if not v:
            raise ValueError('You must agree to the terms and conditions')
        return v


class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordReset(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class EmailVerification(BaseModel):
    """Email verification schema."""
    token: str


class UserSessionResponse(BaseModel):
    """User session response schema."""
    id: UUID
    user_agent: Optional[str]
    ip_address: Optional[str]
    device_info: Optional[Dict[str, Any]]
    created_at: datetime
    last_used: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class UserPreferenceUpdate(BaseModel):
    """User preference update schema."""
    category: str = Field(..., min_length=1, max_length=100)
    key: str = Field(..., min_length=1, max_length=100)
    value: Any


class UserPreferenceResponse(BaseModel):
    """User preference response schema."""
    id: UUID
    category: str
    key: str
    value: Any
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserActivityResponse(BaseModel):
    """User activity response schema."""
    id: UUID
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    ip_address: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response schema."""
    user: UserResponse
    tokens: Token
    message: str = "Authentication successful"


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
