"""
Tarento AI Complaint Tracking System - User Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

from app.utils.constants import UserRole, UserStatus


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.AGENT
    team: Optional[str] = Field(None, max_length=100)
    department_id: Optional[UUID] = None


# Request schemas
class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    org_name: Optional[str] = Field(None, max_length=255)  # For new org creation
    department_id: Optional[UUID] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = Field(None, max_length=255)
    team: Optional[str] = Field(None, max_length=100)
    department_id: Optional[UUID] = None
    current_password: Optional[str] = None  # Required for password change
    new_password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserAdminUpdate(BaseModel):
    """Schema for admin updating user"""
    name: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    team: Optional[str] = Field(None, max_length=100)
    department_id: Optional[UUID] = None
    status: Optional[UserStatus] = None


# Response schemas
class UserResponse(BaseModel):
    """Schema for user response"""
    user_id: UUID
    org_id: UUID
    email: EmailStr
    name: str
    role: UserRole
    team: Optional[str] = None
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserBriefResponse(BaseModel):
    """Brief user info for lists"""
    user_id: UUID
    email: EmailStr
    name: str
    role: UserRole
    team: Optional[str] = None
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    status: UserStatus
    escalations_count: int = 0
    resolutions_count: int = 0
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    items: List[UserBriefResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
