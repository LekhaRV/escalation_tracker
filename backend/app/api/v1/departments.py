from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.api.deps import get_current_user
from app.models import User, Department
from app.schemas.department import DepartmentResponse, DepartmentCreate
from app.core.exceptions import AppError

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get(
    "",
    response_model=List[DepartmentResponse],
    summary="List departments",
    description="Get all departments in the organization with user counts"
)
async def list_departments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all departments for current user's organization"""
    # Get departments with user counts
    result = await db.execute(
        select(
            Department,
            func.count(User.user_id).label('user_count')
        )
        .outerjoin(User, User.department_id == Department.department_id)
        .where(Department.org_id == current_user.org_id)
        .group_by(Department.department_id)
        .order_by(Department.name)
    )
    
    departments = []
    for row in result.all():
        dept = row[0]
        user_count = row[1]
        departments.append({
            "department_id": dept.department_id,
            "org_id": dept.org_id,
            "name": dept.name,
            "description": dept.description,
            "user_count": user_count
        })
    
    return departments


@router.post(
    "",
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
    from app.utils.constants import UserRole
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create departments"
        )
    
    department = Department(
        org_id=current_user.org_id,
        name=data.name,
        description=data.description
    )
    db.add(department)
    await db.commit()
    await db.refresh(department)
    
    return department
