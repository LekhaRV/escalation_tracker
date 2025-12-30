"""
Tarento AI Complaint Tracking System - Auth API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    UserRegister, UserLogin, UserUpdate, TokenResponse,
    TokenRefresh, UserResponse
)
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models import User
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user. If org_name is provided, creates a new organization."
)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user and optionally create organization"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.register(data)
        await db.commit()
        
        return {
            "user": UserResponse.model_validate(result["user"]),
            "tokens": result["tokens"]
        }
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate user and return access + refresh tokens (30min + 7days)"
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access tokens"""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.login(data)
        return tokens
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Use refresh token to get new access + refresh tokens"
)
async def refresh_token(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.refresh_token(data.refresh_token)
        return tokens
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get authenticated user's profile information"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update profile and change password",
    description="Update user profile. Include current_password and new_password to change password."
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile and optionally change password"""
    from app.services.user_service import UserService
    
    user_service = UserService(db)
    
    # Update profile
    user = await user_service.update_user_profile(current_user, data)
    
    # Handle password change if requested
    if data.current_password and data.new_password:
        auth_service = AuthService(db)
        try:
            await auth_service.update_password(
                user,
                data.current_password,
                data.new_password
            )
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    await db.commit()
    return UserResponse.model_validate(user)
