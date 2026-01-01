from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.core.exceptions import NotFoundError, ConflictError

class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_departments(self, org_id: UUID) -> List[Department]:
        """Get all departments for an organization"""
        query = select(Department).where(Department.org_id == org_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_department(self, department_id: UUID) -> Optional[Department]:
        """Get department by ID"""
        query = select(Department).where(Department.department_id == department_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_department(self, data: DepartmentCreate, org_id: UUID) -> Department:
        """Create a new department"""
        # Check if name exists in org
        query = select(Department).where(
            Department.org_id == org_id,
            Department.name == data.name
        )
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise ConflictError(f"Department '{data.name}' already exists")

        department = Department(
            org_id=org_id,
            name=data.name,
            manager_id=data.manager_id
        )
        self.db.add(department)
        await self.db.flush()
        return department
