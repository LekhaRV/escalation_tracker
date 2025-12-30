"""
Tarento AI Complaint Tracking System - Project Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime

from app.utils.constants import ProjectStatus


# Team member schemas
class TeamMemberResponse(BaseModel):
    """Team member response schema"""
    id: UUID
    user_id: UUID
    user_name: str
    user_email: str
    role: str
    specialization: List[str] = []
    is_active: bool
    workload_capacity: int
    current_workload: int
    priority_order: int
    joined_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class TeamMemberManage(BaseModel):
    """Schema for managing team members (add/remove/update)"""
    action: str = Field(..., pattern="^(add|remove|update)$")
    user_id: UUID
    role: Optional[str] = None  # Required for add/update
    specialization: Optional[List[str]] = None
    workload_capacity: Optional[int] = Field(None, ge=1, le=50)
    priority_order: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


# Base project schemas
class ProjectBase(BaseModel):
    """Base project schema"""
    project_name: str = Field(..., min_length=1, max_length=255)
    project_code: Optional[str] = Field(None, max_length=50)
    client_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# Request schemas
class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    project_manager_id: Optional[UUID] = None
    team_lead_id: Optional[UUID] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    project_name: Optional[str] = Field(None, max_length=255)
    project_code: Optional[str] = Field(None, max_length=50)
    client_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    project_manager_id: Optional[UUID] = None
    team_lead_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# Response schemas
class ProjectBriefResponse(BaseModel):
    """Brief project response for lists"""
    project_id: UUID
    org_id: UUID
    project_name: str
    project_code: Optional[str] = None
    client_name: Optional[str] = None
    status: ProjectStatus
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_manager_name: Optional[str] = None
    team_lead_name: Optional[str] = None
    team_count: int = 0
    complaints_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(BaseModel):
    """Detailed project response"""
    project_id: UUID
    org_id: UUID
    project_name: str
    project_code: Optional[str] = None
    client_name: Optional[str] = None
    description: Optional[str] = None
    status: ProjectStatus
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_manager_id: Optional[UUID] = None
    project_manager_name: Optional[str] = None
    team_lead_id: Optional[UUID] = None
    team_lead_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    team_members: List[TeamMemberResponse] = []
    
    # Stats
    complaints_total: int = 0
    complaints_open: int = 0
    complaints_resolved: int = 0
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for paginated project list"""
    items: List[ProjectBriefResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
