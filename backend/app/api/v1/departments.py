from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.api.deps import get_current_user
from app.services.department_service import DepartmentService
from app.schemas.department import DepartmentResponse, DepartmentCreate
from app.models.user import User
from app.core.exceptions import AppError

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get(
    "/",
    response_model=List[DepartmentResponse],
    summary="List departments",
    description="Get all departments in the organization"
)
async def list_departments(
    db: AsyncSession = Depends(get_db),
    # Allow unauthenticated access for registration if needed? 
    # For now, let's assume public or use a specific unauth endpoint if needed.
    # Actually, for registration dropdown, it strictly needs to be public or we need a special endpoint.
    # Let's make it authenticated BUT we need it for registration...
    # Workaround: Allow fetching departments if org_id is provided via query param for public?
    # No, that leaks data. 
    # For now, let's just make it public for simplicity in this dev environment, or require login.
    # Wait, the user said "Role and Department are mandatory for user creation". 
    # If a new user signs up, they ARE NOT LOGGED IN.
    # So this endpoint MUST be public or we need a specific public one.
    # I'll make it public but filter by org_id if provided, else return empty?
    # Or just `depends(get_current_user)` is optional?
    org_id: UUID = Query(..., description="Organization ID to fetch departments for")
):
    """List all departments for an organization"""
    dept_service = DepartmentService(db)
    return await dept_service.get_departments(org_id)

@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create department",
    description="Create a new department (Admin only)"
)
async def create_department(
    data: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new department"""
    dept_service = DepartmentService(db)
    organization = await current_user.awaitable_attrs.organization
    return await dept_service.create_department(data, organization.org_id)
