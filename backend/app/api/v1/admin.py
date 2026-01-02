"""
Tarento AI Complaint Tracking System - Admin API Endpoints
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Organization
from app.schemas import (
    UserCreate, UserAdminUpdate, UserResponse,
    UserBriefResponse, UserListResponse
)
from app.services.user_service import UserService
from app.api.deps import get_current_user, require_admin, require_admin_or_manager, get_current_organization
from app.utils.constants import UserRole, UserStatus
from app.core.exceptions import NotFoundError, ConflictError, AuthorizationError

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List users",
    description="Get all users in organization (admin/manager)"
)
async def list_users(
    role: Optional[UserRole] = Query(None),
    team: Optional[str] = Query(None),
    department_id: Optional[UUID] = Query(None),
    status: Optional[UserStatus] = Query(None),
    search: Optional[str] = Query(None, description="Search by name or email"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db)
):
    """List all users in organization"""
    service = UserService(db)
    result = await service.get_users_with_stats(
        org_id=current_user.org_id,
        role=role,
        team=team,
        department_id=department_id,
        status=status,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    items = [UserBriefResponse.model_validate(u) for u in result["items"]]
    
    return UserListResponse(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"]
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user details",
    description="Get user details by ID"
)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db)
):
    """Get user details"""
    try:
        service = UserService(db)
        user = await service.get_user_by_id(user_id, current_user.org_id)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create new user (admin only)"
)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    try:
        service = UserService(db)
        user = await service.create_user(current_user.org_id, data, current_user)
        await db.commit()
        return UserResponse.model_validate(user)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user (admin can update all fields, manager limited)"
)
async def update_user(
    user_id: UUID,
    data: UserAdminUpdate,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db)
):
    """Update user"""
    try:
        service = UserService(db)
        user = await service.admin_update_user(user_id, current_user.org_id, data, current_user)
        await db.commit()
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/organization",
    summary="Get organization settings",
    description="Get current organization settings and stats"
)
async def get_organization(
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get organization settings"""
    from sqlalchemy import select, func
    from app.models import Complaint, Project
    
    users_count = await db.execute(
        select(func.count()).where(User.org_id == org.org_id)
    )
    projects_count = await db.execute(
        select(func.count()).where(Project.org_id == org.org_id)
    )
    complaints_count = await db.execute(
        select(func.count()).where(Complaint.org_id == org.org_id)
    )
    
    return {
        "org_id": str(org.org_id),
        "org_name": org.org_name,
        "status": org.status.value,
        "email_config": org.email_config,
        "settings": org.settings,
        "stats": {
            "users": users_count.scalar() or 0,
            "projects": projects_count.scalar() or 0,
            "complaints": complaints_count.scalar() or 0
        },
        "created_at": org.created_at.isoformat()
    }


@router.put(
    "/organization",
    summary="Update organization settings",
    description="Update organization settings (admin only)"
)
async def update_organization(
    settings: dict,
    current_user: User = Depends(require_admin),
    org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Update organization settings"""
    if "org_name" in settings:
        org.org_name = settings["org_name"]
    if "email_config" in settings:
        org.email_config = settings["email_config"]
    if "settings" in settings:
        org.settings = settings["settings"]
    
    await db.commit()
    
    return {
        "success": True,
        "org_id": str(org.org_id),
        "org_name": org.org_name
    }
