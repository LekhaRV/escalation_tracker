"""
Tarento AI Complaint Tracking System - Complaints API Endpoints
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User
from app.utils.constants import UserRole
from app.schemas import (
    ComplaintCreate, ComplaintUpdate, ComplaintBulkRequest,
    ComplaintDetailResponse, ComplaintBriefResponse,
    ComplaintListResponse, ComplaintBulkResponse,
    ComplaintCategoryResponse, ComplaintAssignmentResponse,
    ComplaintEscalationResponse, AssignableUserResponse
)
from app.services.complaint_service import ComplaintService
from app.api.deps import get_current_user, require_admin, require_admin_or_manager
from app.utils.constants import ComplaintStatus, SeverityLevel, CATEGORY_DEPARTMENT_MAP
from app.utils.helpers import calculate_assignment_score, get_category_keywords
from app.core.exceptions import NotFoundError, AuthorizationError
from app.models import Project, ProjectTeamMember
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post(
    "/{complaint_id}/recommend-resolution",
    response_model=List[str],
    summary="Get AI resolution steps",
    description="Generate AI-powered resolution recommendations for a complaint"
)
async def recommend_resolution(
    complaint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate resolution recommendations"""
    service = ComplaintService(db)
    try:
        complaint = await service.get_complaint_by_id(complaint_id, current_user.org_id)
        
        category = "General"
        severity = "Medium"
        if complaint.category:
            category = f"{complaint.category.category_type} ({complaint.category.sub_category})"
            severity = complaint.category.severity or "Medium"
            
        steps = await gemini_service.generate_resolution_recommendations(
            subject=complaint.subject,
            description=complaint.description,
            category=category,
            severity=severity
        )
        return steps
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{complaint_id}/assignable-users",
    response_model=List[AssignableUserResponse],
    summary="Get AI-recommended agents",
    description="Get list of agents scored by relevance (skills, workload, project) for this complaint."
)
async def get_assignable_users(
    complaint_id: UUID,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db)
):
    """Get list of users eligible for assignment with AI scores"""
    service = ComplaintService(db)
    
    # 1. Get complaint details with permission check for Managers
    try:
        complaint = await service.get_complaint_by_id(complaint_id, current_user.org_id)
        
        # Enforce Manager Restrictions: Can only see/assign for projects they manage/lead
        if current_user.role == UserRole.MANAGER:
            is_valid_project = False
            # Check if PM or Team Lead
            if complaint.project and (
                complaint.project.project_manager_id == current_user.user_id or 
                complaint.project.team_lead_id == current_user.user_id
            ):
                is_valid_project = True
            
            # Check if project member? (Usually managers manage projects, but requirement says "projects under him")
            # We will stick to PM/Lead check. If strict ownership needed. 
            # Or if they are Department Manager?
            # For now, if project is missing, Manager can't see it? Or generally managers supervise dept?
            # Let's check Dept Manager link.
            # If complaint has no project, can Manager assign? 
            # If compliant is in Manager's department?
            # Let's iterate: PM/Lead OR Dept Manager.
            
            # Simplified for MVP: Check PM/Lead ownership
            if complaint.project_id and not is_valid_project:
                # Extra check: Department Manager
                if hasattr(current_user, 'managed_department') and current_user.managed_department:
                     # If project is in this dept or complaint category is mapped to this dept?
                     # A bit complex. Let's start with strict Project Manager restriction as requested.
                     pass 

            if complaint.project_id and not is_valid_project:
                 raise AuthorizationError("Managers can only assign agents for their own projects")
                 
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Complaint not found")
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
        
    # 2. Determine Scope & Candidates
    candidates = []
    
    # Context for scoring
    severity = SeverityLevel.MEDIUM
    category_type = "support"
    sub_category = ""
    
    if complaint.category:
        severity = complaint.category.severity
        category_type = complaint.category.category_type or "support"
        sub_category = complaint.category.sub_category or ""
        
    severity_val = severity.value if hasattr(severity, "value") else str(severity)
    keywords = get_category_keywords(category_type, sub_category)
    
    # Strategy A: Project Team (Preferred)
    if complaint.project_id:
        # Load project members
        stmt = select(ProjectTeamMember).where(
            ProjectTeamMember.project_id == complaint.project_id,
            ProjectTeamMember.is_active == True
        ).options(selectinload(ProjectTeamMember.user))
        result = await db.execute(stmt)
        team_members = result.scalars().all()
        
        for tm in team_members:
            if not tm.user: continue
            
            # Calculate score
            score = calculate_assignment_score(
                role=tm.role,
                specialization=tm.specialization or [],
                workload=tm.current_workload or 0,
                workload_capacity=tm.workload_capacity or 10,
                severity=severity_val,
                category_keywords=keywords
            )
            
            candidates.append({
                "user": tm.user,
                "score": score,
                "reason": f"Project Member ({tm.role})",
                "workload": tm.current_workload or 0,
                "capacity": tm.workload_capacity or 10
            })
            
    # Strategy B: Department Fallback (if no candidates yet)
    if not candidates:
        target_dept_name = CATEGORY_DEPARTMENT_MAP.get(category_type, "Support")
        
        # Import Department model relative to this file location
        from app.models.department import Department
        
        # Correct Query: Join User -> Department
        stmt = select(User).join(Department, User.department_id == Department.department_id).where(
            User.org_id == current_user.org_id,
            Department.name == target_dept_name,
            User.role.in_([UserRole.AGENT, UserRole.ADMIN, UserRole.MANAGER]),
            User.status == "active"
        )
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        for u in users:
            score = 50.0 # Base score for dept match
            candidates.append({
                "user": u,
                "score": score,
                "reason": f"Department Match ({target_dept_name})",
                "workload": 0,
                "capacity": 10
            })
            
    # Strategy C: Global Fallback (Return ALL active agents if still empty)
    if not candidates:
        # Fetch top 20 active agents/admins to ensure list is never empty
        stmt = select(User).where(
            User.org_id == current_user.org_id,
            User.role.in_([UserRole.AGENT, UserRole.ADMIN, UserRole.MANAGER]),
            User.status == "active"
        ).limit(20)
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        for u in users:
            candidates.append({
                "user": u,
                "score": 10.0, # Low score
                "reason": "General Pool (Fallback)",
                "workload": 0,
                "capacity": 10
            })

    # Sort by score desc
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Build response
    response = []
    for idx, c in enumerate(candidates):
        # Relaxed Recommendation Logic:
        # Mark as recommended if Score >= 50 (Strong Match)
        # OR if they are in the top 3 and Score >= 30 (Decent relative match)
        is_recommended = (c["score"] >= 50) or ((idx < 3) and (c["score"] >= 30))
        
        response.append(AssignableUserResponse(
            user_id=c["user"].user_id,
            name=c["user"].name,
            email=c["user"].email,
            role=c["user"].role,
            match_score=c["score"],
            is_recommended=is_recommended,
            recommendation_reason=c["reason"],
            workload_current=c["workload"],
            workload_capacity=c["capacity"]
        ))
        
    return response


@router.get(
    "",
    response_model=ComplaintListResponse,
    summary="List all complaints",
    description="""
    Get all complaints org-wide. ALL authenticated users see ALL complaints.
    Supports filtering by status, severity, project, assignee, and search.
    """
)
async def list_complaints(
    status: Optional[ComplaintStatus] = Query(None, description="Filter by status"),
    severity: Optional[SeverityLevel] = Query(None, description="Filter by severity"),
    project_id: Optional[UUID] = Query(None, description="Filter by project"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assignee"),
    search: Optional[str] = Query(None, description="Search in subject/description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all complaints with org-wide visibility"""
    service = ComplaintService(db)
    result = await service.get_complaints(
        org_id=current_user.org_id,
        status=status,
        severity=severity,
        project_id=project_id,
        assigned_to=assigned_to,
        search=search,
        page=page,
        page_size=page_size
    )
    
    items = []
    for c in result["items"]:
        item = {
            "complaint_id": c.complaint_id,
            "org_id": c.org_id,
            "project_id": c.project_id,
            "project_name": c.project.project_name if c.project else None,
            "customer_name": c.customer_name,
            "customer_email": c.customer_email,
            "subject": c.subject,
            "status": c.status,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "category_type": c.category.category_type if c.category else None,
            "severity": c.category.severity if c.category else None,
            "assigned_to_name": c.assignment.assigned_user.name if c.assignment and c.assignment.assigned_user else None,
            "sla_deadline": c.assignment.sla_deadline if c.assignment else None
        }
        items.append(ComplaintBriefResponse(**item))
    
    return ComplaintListResponse(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"]
    )


@router.post(
    "",
    response_model=ComplaintDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create complaint",
    description="Create new complaint. Auto-processing: Categorization in 2min, Assignment in 3min if project linked."
)
async def create_complaint(
    data: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new complaint"""
    service = ComplaintService(db)
    complaint = await service.create_complaint(
        org_id=current_user.org_id,
        data=data,
        created_by=current_user
    )
    await db.commit()
    
    # Reload with relations
    complaint = await service.get_complaint_by_id(complaint.complaint_id, current_user.org_id)
    timeline = await service.build_timeline(complaint)
    
    return _build_detail_response(complaint, timeline)


@router.get(
    "/{complaint_id}",
    response_model=ComplaintDetailResponse,
    summary="Get complaint details",
    description="Get complaint with timeline, assignment, escalations, and agent logs."
)
async def get_complaint(
    complaint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complaint details"""
    try:
        service = ComplaintService(db)
        complaint = await service.get_complaint_by_id(complaint_id, current_user.org_id)
        timeline = await service.build_timeline(complaint)
        return _build_detail_response(complaint, timeline)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{complaint_id}",
    response_model=ComplaintDetailResponse,
    summary="Update complaint",
    description="Update complaint - handles status, notes, reassignment (assign_to_user_id), and escalation (escalate_to_level) ALL IN ONE."
)
async def update_complaint(
    complaint_id: UUID,
    data: ComplaintUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update complaint with optional reassignment and escalation"""
    try:
        service = ComplaintService(db)
        complaint = await service.update_complaint(
            complaint_id=complaint_id,
            org_id=current_user.org_id,
            data=data,
            updated_by=current_user
        )
        await db.commit()
        
        complaint = await service.get_complaint_by_id(complaint_id, current_user.org_id)
        timeline = await service.build_timeline(complaint)
        return _build_detail_response(complaint, timeline)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{complaint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete complaint",
    description="Delete complaint (admin only)"
)
async def delete_complaint(
    complaint_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete complaint (admin only)"""
    try:
        service = ComplaintService(db)
        await service.delete_complaint(complaint_id, current_user.org_id, current_user)
        await db.commit()
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/bulk",
    response_model=ComplaintBulkResponse,
    summary="Bulk operations",
    description="Bulk assign, status update, or export multiple complaints"
)
async def bulk_operation(
    data: ComplaintBulkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform bulk operations on complaints"""
    service = ComplaintService(db)
    result = await service.bulk_operation(
        org_id=current_user.org_id,
        data=data,
        performed_by=current_user
    )
    await db.commit()
    return ComplaintBulkResponse(**result)


def _build_detail_response(complaint, timeline):
    """Build detailed complaint response"""
    category = None
    if complaint.category:
        category = ComplaintCategoryResponse(
            category_id=complaint.category.category_id,
            category_type=complaint.category.category_type,
            sub_category=complaint.category.sub_category,
            severity=complaint.category.severity,
            priority=complaint.category.priority,
            department=complaint.category.department,
            confidence_score=float(complaint.category.confidence_score or 0),
            categorized_by=complaint.category.categorized_by,
            categorized_at=complaint.category.categorized_at
        )
    
    assignment = None
    if complaint.assignment:
        assignment = ComplaintAssignmentResponse(
            assignment_id=complaint.assignment.assignment_id,
            assigned_to_user_id=complaint.assignment.assigned_to_user_id,
            assigned_to_team=complaint.assignment.assigned_to_team,
            assigned_user_name=complaint.assignment.assigned_user.name if complaint.assignment.assigned_user else None,
            assignment_reason=complaint.assignment.assignment_reason,
            sla_deadline=complaint.assignment.sla_deadline,
            assigned_by=complaint.assignment.assigned_by,
            assigned_at=complaint.assignment.assigned_at
        )
    
    escalations = []
    for e in complaint.escalations:
        escalations.append(ComplaintEscalationResponse(
            escalation_id=e.escalation_id,
            escalation_level=e.escalation_level,
            escalated_to_user_id=e.escalated_to_user_id,
            escalated_user_name=e.escalated_user.name if e.escalated_user else None,
            escalation_reason=e.escalation_reason,
            escalated_by=e.escalated_by,
            escalated_at=e.escalated_at
        ))
    
    return ComplaintDetailResponse(
        complaint_id=complaint.complaint_id,
        org_id=complaint.org_id,
        project_id=complaint.project_id,
        project_name=complaint.project.project_name if complaint.project else None,
        email_id=complaint.email_id,
        customer_name=complaint.customer_name,
        customer_email=complaint.customer_email,
        customer_phone=complaint.customer_phone,
        subject=complaint.subject,
        description=complaint.description,
        raw_email_content=complaint.raw_email_content,
        status=complaint.status,
        resolution_notes=complaint.resolution_notes,
        resolved_at=complaint.resolved_at,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
        category=category,
        assignment=assignment,
        escalations=escalations,
        timeline=timeline
    )
