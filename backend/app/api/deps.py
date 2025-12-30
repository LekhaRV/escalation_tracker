"""
Tarento AI Complaint Tracking System - API Dependencies
Authentication and authorization dependencies
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Organization
from app.services.auth_service import AuthService
from app.utils.constants import UserRole
from app.core.exceptions import AuthenticationError, AuthorizationError

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.get_current_user(token)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Organization:
    """Get current user's organization"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Organization).where(Organization.org_id == current_user.org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return org


def require_role(allowed_roles: List[UserRole]):
    """Dependency factory for role-based access control"""
    
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    
    return role_checker


# Convenience dependencies for common role checks
require_admin = require_role([UserRole.ADMIN])
require_admin_or_manager = require_role([UserRole.ADMIN, UserRole.MANAGER])
require_any_editor = require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT])
