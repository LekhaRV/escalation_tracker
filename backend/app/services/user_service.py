"""
Tarento AI Complaint Tracking System - User Service
User management operations
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import User
from app.schemas import UserCreate, UserUpdate, UserAdminUpdate, UserBriefResponse
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundError, ConflictError, AuthorizationError
from app.utils.constants import UserRole, UserStatus


class UserService:
    """User management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: UUID, org_id: UUID) -> User:
        """Get user by ID within organization"""
        result = await self.db.execute(
            select(User).where(
                User.user_id == user_id,
                User.org_id == org_id
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        
        return user
    
    async def get_users(
        self,
        org_id: UUID,
        role: Optional[UserRole] = None,
        team: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[UserStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """Get paginated list of users in organization"""
        query = select(User).where(User.org_id == org_id)
        
        if role:
            query = query.where(User.role == role)
        if team:
            query = query.where(User.team == team)
        if department:
            query = query.where(User.department == department)
        if status:
            query = query.where(User.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return {
            "items": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def create_user(
        self,
        org_id: UUID,
        data: UserCreate,
        created_by: User
    ) -> User:
        """Create a new user (admin only)"""
        # Only admin can create users
        if created_by.role != UserRole.ADMIN:
            raise AuthorizationError("Only admins can create users")
        
        # Check if email already exists
        existing = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"User with email {data.email} already exists")
        
        user = User(
            org_id=org_id,
            email=data.email,
            password=get_password_hash(data.password),
            name=data.name,
            role=data.role,
            team=data.team,
            department=data.department,
            status=UserStatus.ACTIVE
        )
        
        self.db.add(user)
        await self.db.flush()
        
        return user
    
    async def update_user_profile(
        self,
        user: User,
        data: UserUpdate
    ) -> User:
        """Update user's own profile"""
        if data.name is not None:
            user.name = data.name
        if data.team is not None:
            user.team = data.team
        if data.department is not None:
            user.department = data.department
        
        await self.db.flush()
        return user
    
    async def admin_update_user(
        self,
        user_id: UUID,
        org_id: UUID,
        data: UserAdminUpdate,
        updated_by: User
    ) -> User:
        """Admin/Manager update user"""
        user = await self.get_user_by_id(user_id, org_id)
        
        # Check permissions
        if updated_by.role == UserRole.ADMIN:
            # Admin can update everything
            pass
        elif updated_by.role == UserRole.MANAGER:
            # Manager can update limited fields, not roles
            if data.role is not None:
                raise AuthorizationError("Managers cannot change user roles")
            if data.status is not None:
                raise AuthorizationError("Managers cannot change user status")
        else:
            raise AuthorizationError("Not authorized to update users")
        
        # Apply updates
        if data.name is not None:
            user.name = data.name
        if data.role is not None:
            user.role = data.role
        if data.team is not None:
            user.team = data.team
        if data.department is not None:
            user.department = data.department
        if data.status is not None:
            user.status = data.status
        
        await self.db.flush()
        return user
    
    async def get_users_by_department(
        self,
        org_id: UUID,
        department: str
    ) -> List[User]:
        """Get active users in a department"""
        result = await self.db.execute(
            select(User).where(
                User.org_id == org_id,
                User.department == department,
                User.status == UserStatus.ACTIVE
            )
        )
        return result.scalars().all()
    
    async def get_user_workload(self, user_id: UUID) -> int:
        """Get current workload (active complaints assigned)"""
        from app.models import ComplaintAssignment, Complaint
        from app.utils.constants import ComplaintStatus
        
        result = await self.db.execute(
            select(func.count()).select_from(ComplaintAssignment).join(
                Complaint, ComplaintAssignment.complaint_id == Complaint.complaint_id
            ).where(
                ComplaintAssignment.assigned_to_user_id == user_id,
                Complaint.status.in_([ComplaintStatus.NEW, ComplaintStatus.CATEGORIZED, ComplaintStatus.IN_PROGRESS])
            )
        )
        return result.scalar() or 0
