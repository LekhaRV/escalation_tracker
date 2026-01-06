"""
Tarento AI Complaint Tracking System - Complaint Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

from app.utils.constants import ComplaintStatus, SeverityLevel


# Category schemas
class ComplaintCategoryResponse(BaseModel):
    """Category response schema"""
    category_id: UUID
    category_type: str
    sub_category: Optional[str] = None
    severity: SeverityLevel
    priority: int
    department: Optional[str] = None
    confidence_score: float
    categorized_by: str
    categorized_at: datetime
    
    class Config:
        from_attributes = True


# Assignment schemas
class ComplaintAssignmentResponse(BaseModel):
    """Assignment response schema"""
    assignment_id: UUID
    assigned_to_user_id: Optional[UUID] = None
    assigned_to_team: Optional[str] = None
    assigned_user_name: Optional[str] = None
    assignment_reason: Optional[str] = None
    sla_deadline: datetime
    assigned_by: str
    assigned_at: datetime
    
    class Config:
        from_attributes = True


# Escalation schemas
class ComplaintEscalationResponse(BaseModel):
    """Escalation response schema"""
    escalation_id: UUID
    escalation_level: int
    escalated_to_user_id: Optional[UUID] = None
    escalated_user_name: Optional[str] = None
    escalation_reason: Optional[str] = None
    escalated_by: str
    escalated_at: datetime
    
    class Config:
        from_attributes = True


class AssignableUserResponse(BaseModel):
    """Schema for users to assign to a complaint with AI scoring"""
    user_id: UUID
    name: str
    email: str
    role: str
    match_score: float
    is_recommended: bool
    recommendation_reason: Optional[str] = None
    workload_current: int
    workload_capacity: int


# Base complaint schemas
class ComplaintBase(BaseModel):
    """Base complaint schema"""
    subject: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    ai_summary: Optional[str] = None
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = Field(None, max_length=50)
    project_id: Optional[UUID] = None


# Request schemas
class ComplaintCreate(ComplaintBase):
    """Schema for creating a complaint"""
    pass


class ComplaintUpdate(BaseModel):
    """Schema for updating a complaint (combined: update, assign, escalate)"""
    # Basic updates
    subject: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[ComplaintStatus] = None
    resolution_notes: Optional[str] = None
    project_id: Optional[UUID] = None
    
    # Assignment (reassignment)
    assign_to_user_id: Optional[UUID] = None
    
    # Escalation
    escalate_to_level: Optional[int] = Field(None, ge=1, le=3)
    escalate_reason: Optional[str] = None


class ComplaintBulkRequest(BaseModel):
    """Schema for bulk operations"""
    action: str = Field(..., pattern="^(assign|update_status|export)$")
    complaint_ids: List[UUID]
    # For assign action
    assign_to_user_id: Optional[UUID] = None
    # For update_status action
    status: Optional[ComplaintStatus] = None
    # For export action
    format: Optional[str] = Field(None, pattern="^(csv|excel|pdf)$")


# Response schemas
class ComplaintBriefResponse(BaseModel):
    """Brief complaint response for lists"""
    complaint_id: UUID
    org_id: UUID
    project_id: Optional[UUID] = None
    project_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    subject: str
    status: ComplaintStatus
    created_at: datetime
    updated_at: datetime
    # Category info
    category_type: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    # Assignment info
    assigned_to_name: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Comment schemas
class ComplaintCommentResponse(BaseModel):
    """Comment response schema"""
    comment_id: UUID
    complaint_id: UUID
    user_id: Optional[UUID] = None
    user_name: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ComplaintCommentCreate(BaseModel):
    """Schema for creating a comment"""
    content: str = Field(..., min_length=1)


class ComplaintDetailResponse(BaseModel):
    """Detailed complaint response"""
    complaint_id: UUID

    org_id: UUID
    project_id: Optional[UUID] = None
    project_name: Optional[str] = None
    email_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    subject: str
    description: Optional[str] = None
    ai_summary: Optional[str] = None
    raw_email_content: Optional[str] = None
    status: ComplaintStatus
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    category: Optional[ComplaintCategoryResponse] = None
    assignment: Optional[ComplaintAssignmentResponse] = None
    escalations: List[ComplaintEscalationResponse] = []
    comments: List[ComplaintCommentResponse] = []
    
    # Timeline (combined history)
    timeline: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


class ComplaintListResponse(BaseModel):
    """Schema for paginated complaint list"""
    items: List[ComplaintBriefResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ComplaintBulkResponse(BaseModel):
    """Response for bulk operations"""
    success: bool
    processed: int
    failed: int
    errors: List[Dict[str, Any]] = []
    # For export
    download_url: Optional[str] = None
