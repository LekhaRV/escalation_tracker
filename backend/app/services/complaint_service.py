"""
Tarento AI Complaint Tracking System - Complaint Service
Complaint management operations
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models import (
    Complaint, ComplaintCategory, ComplaintAssignment,
    ComplaintEscalation, Project, User, AgentLog
)
from app.schemas import (
    ComplaintCreate, ComplaintUpdate, ComplaintBulkRequest,
    ComplaintDetailResponse
)
from app.core.exceptions import NotFoundError, AuthorizationError
from app.utils.constants import (
    ComplaintStatus, SeverityLevel, UserRole, AgentLogStatus
)
from app.utils.helpers import calculate_sla_deadline


class ComplaintService:
    """Complaint management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_complaint_by_id(
        self,
        complaint_id: UUID,
        org_id: UUID,
        include_relations: bool = True
    ) -> Complaint:
        """Get complaint by ID with optional relations"""
        query = select(Complaint).where(
            Complaint.complaint_id == complaint_id,
            Complaint.org_id == org_id
        )
        
        if include_relations:
            query = query.options(
                selectinload(Complaint.category),
                selectinload(Complaint.assignment).selectinload(ComplaintAssignment.assigned_user),
                selectinload(Complaint.escalations).selectinload(ComplaintEscalation.escalated_user),
                selectinload(Complaint.project),
                selectinload(Complaint.agent_logs)
            )
        
        result = await self.db.execute(query)
        complaint = result.scalar_one_or_none()
        
        if not complaint:
            raise NotFoundError(f"Complaint {complaint_id} not found")
        
        return complaint
    
    async def get_complaints(
        self,
        org_id: UUID,
        status: Optional[ComplaintStatus] = None,
        severity: Optional[SeverityLevel] = None,
        project_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """Get paginated list of complaints (org-wide visibility)"""
        query = select(Complaint).where(Complaint.org_id == org_id)
        
        # Apply filters
        if status:
            query = query.where(Complaint.status == status)
        if project_id:
            query = query.where(Complaint.project_id == project_id)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Complaint.subject.ilike(search_term),
                    Complaint.description.ilike(search_term),
                    Complaint.customer_name.ilike(search_term),
                    Complaint.customer_email.ilike(search_term)
                )
            )
        
        # Join with category for severity filter
        if severity:
            query = query.join(
                ComplaintCategory,
                Complaint.complaint_id == ComplaintCategory.complaint_id,
                isouter=True
            ).where(ComplaintCategory.severity == severity)
        
        # Join with assignment for assigned_to filter
        if assigned_to:
            query = query.join(
                ComplaintAssignment,
                Complaint.complaint_id == ComplaintAssignment.complaint_id,
                isouter=True
            ).where(ComplaintAssignment.assigned_to_user_id == assigned_to)
        
        # Add common joins for response data
        query = query.options(
            selectinload(Complaint.category),
            selectinload(Complaint.assignment).selectinload(ComplaintAssignment.assigned_user),
            selectinload(Complaint.project)
        )
        
        # Get total count
        count_query = select(func.count()).select_from(
            select(Complaint.complaint_id).where(Complaint.org_id == org_id).subquery()
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Complaint.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        complaints = result.scalars().unique().all()
        
        return {
            "items": complaints,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def create_complaint(
        self,
        org_id: UUID,
        data: ComplaintCreate,
        created_by: Optional[User] = None
    ) -> Complaint:
        """Create a new complaint"""
        complaint = Complaint(
            org_id=org_id,
            project_id=data.project_id,
            customer_name=data.customer_name,
            customer_email=data.customer_email,
            customer_phone=data.customer_phone,
            subject=data.subject,
            description=data.description,
            status=ComplaintStatus.NEW
        )
        
        self.db.add(complaint)
        await self.db.flush()
        
        return complaint
    
    async def update_complaint(
        self,
        complaint_id: UUID,
        org_id: UUID,
        data: ComplaintUpdate,
        updated_by: User
    ) -> Complaint:
        """
        Update complaint - handles status update, reassignment, and escalation
        All in one endpoint as per requirements
        """
        complaint = await self.get_complaint_by_id(complaint_id, org_id)
        
        # Check permissions based on role
        if updated_by.role == UserRole.VIEWER:
            raise AuthorizationError("Viewers cannot update complaints")
            
        # Agent Permission Logic
        if updated_by.role == UserRole.AGENT:
            # 1. Assignment Check
            is_assigned_to_me = (
                complaint.assignment and 
                complaint.assignment.assigned_to_user_id == updated_by.user_id
            )
            
            # 2. Check if trying to assign
            if data.assign_to_user_id:
                # Agents can only PICK UP (assign to self)
                if data.assign_to_user_id != updated_by.user_id:
                    raise AuthorizationError("Agents can only assign complaints to themselves (Pick Up)")
                # Allowed: Picking up unassigned or stealing? usually pick up unassigned.
                # Let's assume re-claiming is allowed if they are the assignee? No, if assigned to someone else, can they steal?
                # Stricter: Can only pick up if unassigned OR if it's already assigned to them (no-op)
                if complaint.assignment and complaint.assignment.assigned_to_user_id and complaint.assignment.assigned_to_user_id != updated_by.user_id:
                     raise AuthorizationError("Complaint is already assigned to another agent")

            # 3. Check if trying to update other fields (status, notes, etc)
            # If we are updating content, we MUST be the assignee.
            # Exception: We are becoming the assignee in this very request (Pick up + Update)
            becoming_assignee = (data.assign_to_user_id == updated_by.user_id)
            
            if (data.status or data.resolution_notes or data.escalate_to_level or data.subject or data.description):
                if not is_assigned_to_me and not becoming_assignee:
                    raise AuthorizationError("Agents can only update complaints assigned to them")

        # Basic updates (status, notes, etc.)
        if data.subject is not None:
            complaint.subject = data.subject
        if data.description is not None:
            complaint.description = data.description
        if data.project_id is not None:
            complaint.project_id = data.project_id
        if data.resolution_notes is not None:
            complaint.resolution_notes = data.resolution_notes
        
        # Status update
        if data.status is not None:
            # Agents can only update to certain statuses
            if updated_by.role == UserRole.AGENT:
                allowed_statuses = [
                    ComplaintStatus.IN_PROGRESS,
                    ComplaintStatus.RESOLVED
                ]
                if data.status not in allowed_statuses:
                    raise AuthorizationError(
                        f"Agents can only update status to: {[s.value for s in allowed_statuses]}"
                    )
            
            complaint.status = data.status
            
            if data.status == ComplaintStatus.RESOLVED:
                complaint.resolved_at = datetime.utcnow()
        
        # Reassignment
        if data.assign_to_user_id is not None:
            # Agent self-assignment check is already done above
            
            await self._reassign_complaint(
                complaint,
                data.assign_to_user_id,
                updated_by
            )
        
        # Escalation
        if data.escalate_to_level is not None:
            await self._escalate_complaint(
                complaint,
                data.escalate_to_level,
                data.escalate_reason,
                updated_by
            )
        
        await self.db.flush()
        return complaint
    
    async def _reassign_complaint(
        self,
        complaint: Complaint,
        new_user_id: UUID,
        assigned_by: User
    ):
        """Reassign complaint to a new user"""
        from app.models import User as UserModel
        
        # Verify new user exists
        result = await self.db.execute(
            select(UserModel).where(
                UserModel.user_id == new_user_id,
                UserModel.org_id == complaint.org_id
            )
        )
        new_user = result.scalar_one_or_none()
        if not new_user:
            raise NotFoundError(f"User {new_user_id} not found")
        
        # Get severity for SLA calculation
        severity = SeverityLevel.MEDIUM
        if complaint.category:
            severity = complaint.category.severity
        
        # Update or create assignment
        if complaint.assignment:
            complaint.assignment.assigned_to_user_id = new_user_id
            complaint.assignment.assignment_reason = f"Reassigned by {assigned_by.name}"
            complaint.assignment.assigned_by = assigned_by.role.value
            complaint.assignment.assigned_at = datetime.utcnow()
        else:
            assignment = ComplaintAssignment(
                complaint_id=complaint.complaint_id,
                assigned_to_user_id=new_user_id,
                assignment_reason=f"Assigned by {assigned_by.name}",
                sla_deadline=calculate_sla_deadline(severity.value),
                assigned_by=assigned_by.role.value
            )
            self.db.add(assignment)
    
    async def _escalate_complaint(
        self,
        complaint: Complaint,
        level: int,
        reason: Optional[str],
        escalated_by: User
    ):
        """Escalate complaint to a higher level"""
        # Find escalation target (project manager or department manager)
        escalation_user_id = None
        
        if complaint.project_id and complaint.project:
            if level == 1:
                escalation_user_id = complaint.project.team_lead_id
            elif level >= 2:
                escalation_user_id = complaint.project.project_manager_id
        
        escalation = ComplaintEscalation(
            complaint_id=complaint.complaint_id,
            escalation_level=level,
            escalated_to_user_id=escalation_user_id,
            escalation_reason=reason or f"Escalated to level {level}",
            escalated_by=escalated_by.role.value
        )
        
        self.db.add(escalation)
    
    async def delete_complaint(
        self,
        complaint_id: UUID,
        org_id: UUID,
        deleted_by: User
    ) -> bool:
        """Delete complaint (admin only)"""
        if deleted_by.role != UserRole.ADMIN:
            raise AuthorizationError("Only admins can delete complaints")
        
        complaint = await self.get_complaint_by_id(complaint_id, org_id, include_relations=False)
        
        await self.db.delete(complaint)
        await self.db.flush()
        
        return True
    
    async def bulk_operation(
        self,
        org_id: UUID,
        data: ComplaintBulkRequest,
        performed_by: User
    ) -> dict:
        """Perform bulk operations on complaints"""
        results = {
            "success": True,
            "processed": 0,
            "failed": 0,
            "errors": []
        }
        
        for complaint_id in data.complaint_ids:
            try:
                if data.action == "assign":
                    await self.update_complaint(
                        complaint_id,
                        org_id,
                        ComplaintUpdate(assign_to_user_id=data.assign_to_user_id),
                        performed_by
                    )
                elif data.action == "update_status":
                    await self.update_complaint(
                        complaint_id,
                        org_id,
                        ComplaintUpdate(status=data.status),
                        performed_by
                    )
                
                results["processed"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "complaint_id": str(complaint_id),
                    "error": str(e)
                })
        
        if results["failed"] > 0:
            results["success"] = False
        
        return results
    
    async def build_timeline(self, complaint: Complaint) -> List[Dict[str, Any]]:
        """Build complaint timeline from various events"""
        timeline = []
        
        # Created event
        timeline.append({
            "type": "created",
            "timestamp": complaint.created_at.isoformat(),
            "description": "Complaint created"
        })
        
        # Categorization event
        if complaint.category:
            timeline.append({
                "type": "categorized",
                "timestamp": complaint.category.categorized_at.isoformat(),
                "description": f"Categorized as {complaint.category.category_type} ({complaint.category.severity.value})"
            })
        
        # Assignment event
        if complaint.assignment:
            user_name = "Unknown"
            if complaint.assignment.assigned_user:
                user_name = complaint.assignment.assigned_user.name
            timeline.append({
                "type": "assigned",
                "timestamp": complaint.assignment.assigned_at.isoformat(),
                "description": f"Assigned to {user_name}"
            })
        
        # Escalation events
        for esc in complaint.escalations:
            user_name = "Unknown"
            if esc.escalated_user:
                user_name = esc.escalated_user.name
            timeline.append({
                "type": "escalated",
                "timestamp": esc.escalated_at.isoformat(),
                "description": f"Escalated to level {esc.escalation_level} ({user_name})"
            })
        
        # Resolution event
        if complaint.resolved_at:
            timeline.append({
                "type": "resolved",
                "timestamp": complaint.resolved_at.isoformat(),
                "description": "Complaint resolved"
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        
        return timeline
