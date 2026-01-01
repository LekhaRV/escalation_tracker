"""
Tarento AI Complaint Tracking System - Projects API Endpoints
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import (
    ProjectCreate, ProjectUpdate, TeamMemberManage,
    ProjectDetailResponse, ProjectBriefResponse,
    ProjectListResponse, TeamMemberResponse
)
from app.services.project_service import ProjectService
from app.api.deps import get_current_user, require_admin_or_manager
from app.utils.constants import ProjectStatus
from app.core.exceptions import NotFoundError, AuthorizationError, ConflictError

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List all projects",
    description="Get all projects org-wide. ALL authenticated users see ALL projects."
)
async def list_projects(
    status: Optional[ProjectStatus] = Query(None),
    client_name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all projects with org-wide visibility"""
    service = ProjectService(db)
    result = await service.get_projects(
        org_id=current_user.org_id,
        status=status,
        client_name=client_name,
        page=page,
        page_size=page_size
    )
    
    items = []
    for p in result["items"]:
        items.append(ProjectBriefResponse(
            project_id=p.project_id,
            org_id=p.org_id,
            project_name=p.project_name,
            project_code=p.project_code,
            client_name=p.client_name,
            status=p.status,
            start_date=p.start_date,
            end_date=p.end_date,
            project_manager_name=p.project_manager.name if p.project_manager else None,
            team_lead_name=p.team_lead.name if p.team_lead else None,
            department_id=p.department_id,
            department_name=p.department.name if p.department else None,
            team_count=getattr(p, 'team_count', len(p.team_members)),
            complaints_count=getattr(p, 'complaints_count', 0),
            created_at=p.created_at
        ))
    
    return ProjectListResponse(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"]
    )


@router.post(
    "",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Create new project (admin/manager only)"
)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    try:
        service = ProjectService(db)
        project = await service.create_project(
            org_id=current_user.org_id,
            data=data,
            created_by=current_user
        )
        await db.commit()
        
        project = await service.get_project_by_id(project.project_id, current_user.org_id)
        stats = await service.get_project_stats(project.project_id)
        return _build_detail_response(project, stats)
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get project details",
    description="Get project with team members and complaint stats"
)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project details"""
    try:
        service = ProjectService(db)
        project = await service.get_project_by_id(project_id, current_user.org_id)
        stats = await service.get_project_stats(project_id)
        return _build_detail_response(project, stats)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Update project",
    description="Update project details (admin/manager only)"
)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db)
):
    """Update project"""
    try:
        service = ProjectService(db)
        project = await service.update_project(project_id, current_user.org_id, data, current_user)
        await db.commit()
        
        project = await service.get_project_by_id(project_id, current_user.org_id)
        stats = await service.get_project_stats(project_id)
        return _build_detail_response(project, stats)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put(
    "/{project_id}/team",
    response_model=ProjectDetailResponse,
    summary="Manage team",
    description="Add/remove/update team members. action=add|remove|update"
)
async def manage_team(
    project_id: UUID,
    data: TeamMemberManage,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db)
):
    """Manage project team members"""
    try:
        service = ProjectService(db)
        project = await service.manage_team(project_id, current_user.org_id, data, current_user)
        await db.commit()
        stats = await service.get_project_stats(project_id)
        return _build_detail_response(project, stats)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


def _build_detail_response(project, stats):
    """Build detailed project response"""
    team_members = []
    for m in project.team_members:
        team_members.append(TeamMemberResponse(
            id=m.id,
            user_id=m.user_id,
            user_name=m.user.name if m.user else "Unknown",
            user_email=m.user.email if m.user else "",
            role=m.role,
            specialization=m.specialization or [],
            is_active=m.is_active,
            workload_capacity=m.workload_capacity,
            current_workload=m.current_workload,
            priority_order=m.priority_order,
            joined_at=m.joined_at
        ))
    
    return ProjectDetailResponse(
        project_id=project.project_id,
        org_id=project.org_id,
        project_name=project.project_name,
        project_code=project.project_code,
        client_name=project.client_name,
        description=project.description,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        project_manager_id=project.project_manager_id,
        project_manager_name=project.project_manager.name if project.project_manager else None,
        team_lead_id=project.team_lead_id,
        team_lead_name=project.team_lead.name if project.team_lead else None,
        department_id=project.department_id,
        department_name=project.department.name if project.department else None,
        created_at=project.created_at,
        updated_at=project.updated_at,
        team_members=team_members,
        complaints_total=stats["complaints_total"],
        complaints_open=stats["complaints_open"],
        complaints_resolved=stats["complaints_resolved"]
    )
