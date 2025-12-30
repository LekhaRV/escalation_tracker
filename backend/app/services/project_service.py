"""
Tarento AI Complaint Tracking System - Project Service
Project management operations
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models import Project, ProjectTeamMember, User, Complaint
from app.schemas import ProjectCreate, ProjectUpdate, TeamMemberManage
from app.core.exceptions import NotFoundError, AuthorizationError, ConflictError
from app.utils.constants import ProjectStatus, UserRole, ComplaintStatus


class ProjectService:
    """Project management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_project_by_id(
        self,
        project_id: UUID,
        org_id: UUID,
        include_relations: bool = True
    ) -> Project:
        """Get project by ID with optional relations"""
        query = select(Project).where(
            Project.project_id == project_id,
            Project.org_id == org_id
        )
        
        if include_relations:
            query = query.options(
                selectinload(Project.project_manager),
                selectinload(Project.team_lead),
                selectinload(Project.team_members).selectinload(ProjectTeamMember.user)
            )
        
        result = await self.db.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        
        return project
    
    async def get_projects(
        self,
        org_id: UUID,
        status: Optional[ProjectStatus] = None,
        client_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """Get paginated list of projects (org-wide visibility)"""
        query = select(Project).where(Project.org_id == org_id)
        
        if status:
            query = query.where(Project.status == status)
        if client_name:
            query = query.where(Project.client_name.ilike(f"%{client_name}%"))
        
        query = query.options(
            selectinload(Project.project_manager),
            selectinload(Project.team_lead),
            selectinload(Project.team_members)
        )
        
        # Get total count
        count_query = select(func.count()).select_from(
            select(Project.project_id).where(Project.org_id == org_id).subquery()
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(Project.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        projects = result.scalars().unique().all()
        
        # Add complaint counts
        projects_with_counts = []
        for project in projects:
            count_result = await self.db.execute(
                select(func.count()).where(Complaint.project_id == project.project_id)
            )
            complaint_count = count_result.scalar() or 0
            project.complaints_count = complaint_count
            project.team_count = len(project.team_members)
            projects_with_counts.append(project)
        
        return {
            "items": projects_with_counts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def create_project(
        self,
        org_id: UUID,
        data: ProjectCreate,
        created_by: User
    ) -> Project:
        """Create a new project"""
        if created_by.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise AuthorizationError("Only admins and managers can create projects")
        
        project = Project(
            org_id=org_id,
            project_name=data.project_name,
            project_code=data.project_code,
            client_name=data.client_name,
            description=data.description,
            status=data.status,
            project_manager_id=data.project_manager_id,
            team_lead_id=data.team_lead_id,
            start_date=data.start_date,
            end_date=data.end_date
        )
        
        self.db.add(project)
        await self.db.flush()
        
        return project
    
    async def update_project(
        self,
        project_id: UUID,
        org_id: UUID,
        data: ProjectUpdate,
        updated_by: User
    ) -> Project:
        """Update project details"""
        if updated_by.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise AuthorizationError("Only admins and managers can update projects")
        
        project = await self.get_project_by_id(project_id, org_id, include_relations=False)
        
        if data.project_name is not None:
            project.project_name = data.project_name
        if data.project_code is not None:
            project.project_code = data.project_code
        if data.client_name is not None:
            project.client_name = data.client_name
        if data.description is not None:
            project.description = data.description
        if data.status is not None:
            project.status = data.status
        if data.project_manager_id is not None:
            project.project_manager_id = data.project_manager_id
        if data.team_lead_id is not None:
            project.team_lead_id = data.team_lead_id
        if data.start_date is not None:
            project.start_date = data.start_date
        if data.end_date is not None:
            project.end_date = data.end_date
        
        await self.db.flush()
        return project
    
    async def manage_team(
        self,
        project_id: UUID,
        org_id: UUID,
        data: TeamMemberManage,
        managed_by: User
    ) -> Project:
        """Add, remove, or update team members"""
        if managed_by.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise AuthorizationError("Only admins and managers can manage project teams")
        
        project = await self.get_project_by_id(project_id, org_id)
        
        # Verify user exists
        result = await self.db.execute(
            select(User).where(
                User.user_id == data.user_id,
                User.org_id == org_id
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError(f"User {data.user_id} not found")
        
        if data.action == "add":
            # Check if already a member
            existing = await self.db.execute(
                select(ProjectTeamMember).where(
                    ProjectTeamMember.project_id == project_id,
                    ProjectTeamMember.user_id == data.user_id
                )
            )
            if existing.scalar_one_or_none():
                raise ConflictError("User is already a team member")
            
            if not data.role:
                raise AuthorizationError("Role is required when adding team member")
            
            member = ProjectTeamMember(
                project_id=project_id,
                user_id=data.user_id,
                role=data.role,
                specialization=data.specialization or [],
                workload_capacity=data.workload_capacity or 10,
                priority_order=data.priority_order or 1,
                is_active=True
            )
            self.db.add(member)
        
        elif data.action == "remove":
            result = await self.db.execute(
                select(ProjectTeamMember).where(
                    ProjectTeamMember.project_id == project_id,
                    ProjectTeamMember.user_id == data.user_id
                )
            )
            member = result.scalar_one_or_none()
            if not member:
                raise NotFoundError("User is not a team member")
            
            await self.db.delete(member)
        
        elif data.action == "update":
            result = await self.db.execute(
                select(ProjectTeamMember).where(
                    ProjectTeamMember.project_id == project_id,
                    ProjectTeamMember.user_id == data.user_id
                )
            )
            member = result.scalar_one_or_none()
            if not member:
                raise NotFoundError("User is not a team member")
            
            if data.role is not None:
                member.role = data.role
            if data.specialization is not None:
                member.specialization = data.specialization
            if data.workload_capacity is not None:
                member.workload_capacity = data.workload_capacity
            if data.priority_order is not None:
                member.priority_order = data.priority_order
            if data.is_active is not None:
                member.is_active = data.is_active
        
        await self.db.flush()
        
        # Reload project with updated team
        return await self.get_project_by_id(project_id, org_id)
    
    async def get_project_stats(self, project_id: UUID) -> dict:
        """Get complaint statistics for a project"""
        total = await self.db.execute(
            select(func.count()).where(Complaint.project_id == project_id)
        )
        
        open_complaints = await self.db.execute(
            select(func.count()).where(
                Complaint.project_id == project_id,
                Complaint.status.in_([
                    ComplaintStatus.NEW,
                    ComplaintStatus.CATEGORIZED,
                    ComplaintStatus.IN_PROGRESS
                ])
            )
        )
        
        resolved = await self.db.execute(
            select(func.count()).where(
                Complaint.project_id == project_id,
                Complaint.status.in_([
                    ComplaintStatus.RESOLVED,
                    ComplaintStatus.CLOSED
                ])
            )
        )
        
        return {
            "complaints_total": total.scalar() or 0,
            "complaints_open": open_complaints.scalar() or 0,
            "complaints_resolved": resolved.scalar() or 0
        }
    
    async def get_project_team_for_routing(
        self,
        project_id: UUID
    ) -> List[ProjectTeamMember]:
        """Get active team members for complaint routing"""
        result = await self.db.execute(
            select(ProjectTeamMember)
            .where(
                ProjectTeamMember.project_id == project_id,
                ProjectTeamMember.is_active == True
            )
            .options(selectinload(ProjectTeamMember.user))
            .order_by(ProjectTeamMember.priority_order)
        )
        return result.scalars().all()
