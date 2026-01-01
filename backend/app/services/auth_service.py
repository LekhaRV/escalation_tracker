"""
Tarento AI Complaint Tracking System - Auth Service
Authentication and authorization logic
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import User, Organization
from app.schemas import UserRegister, UserLogin, TokenResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_tokens,
    decode_token
)
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError
)
from app.utils.constants import UserRole, UserStatus, OrgStatus


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, data: UserRegister) -> dict:
        """Register a new user (and optionally create organization)"""
        # Check if email already exists
        existing = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"User with email {data.email} already exists")
        
        # Create or get organization
        if data.org_name:
            # Create new organization
            org = Organization(
                org_name=data.org_name,
                status=OrgStatus.ACTIVE
            )
            self.db.add(org)
            await self.db.flush()
            role = UserRole.ADMIN  # First user of org is admin
        else:
            # Join default organization (or error)
            result = await self.db.execute(
                select(Organization).where(Organization.status == OrgStatus.ACTIVE).limit(1)
            )
            org = result.scalar_one_or_none()
            if not org:
                raise NotFoundError("No organization available. Please provide org_name to create one.")
            role = UserRole.AGENT
        
        # Create user
        user = User(
            org_id=org.org_id,
            email=data.email,
            password=get_password_hash(data.password),
            name=data.name,
            role=role,
            status=UserStatus.ACTIVE,
            department_id=data.department_id
        )
        self.db.add(user)
        await self.db.flush()
        
        # Generate tokens
        tokens = create_tokens(user.user_id, org.org_id)
        
        return {
            "user": user,
            "tokens": tokens
        }
    
    async def login(self, data: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens"""
        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == data.email).options(selectinload(User.department_link))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Verify password
        if not verify_password(data.password, user.password):
            raise AuthenticationError("Invalid email or password")
        
        # Check user status
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("User account is inactive")
        
        # Generate tokens
        tokens = create_tokens(user.user_id, user.org_id)
        
        return TokenResponse(**tokens)
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        payload = decode_token(refresh_token)
        
        if not payload:
            raise AuthenticationError("Invalid refresh token")
        
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        
        if not user_id or not org_id:
            raise AuthenticationError("Invalid token payload")
        
        # Verify user still exists and is active
        result = await self.db.execute(
            select(User).where(User.user_id == UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or user.status != UserStatus.ACTIVE:
            raise AuthenticationError("User not found or inactive")
        
        # Generate new tokens
        tokens = create_tokens(user.user_id, user.org_id)
        
        return TokenResponse(**tokens)
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        payload = decode_token(token)
        
        if not payload:
            raise AuthenticationError("Invalid token")
        
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type")
        
        user_id = payload.get("sub")
        
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        
        result = await self.db.execute(
            select(User).where(User.user_id == UUID(user_id)).options(selectinload(User.department_link))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("User not found")
        
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("User account is inactive")
        
        return user
    
    async def update_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """Update user password"""
        if not verify_password(current_password, user.password):
            raise AuthenticationError("Current password is incorrect")
        
        user.password = get_password_hash(new_password)
        await self.db.flush()
        
        return True
