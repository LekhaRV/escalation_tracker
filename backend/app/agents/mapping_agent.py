"""
Tarento AI Complaint Tracking System - Mapping Agent
Project-based intelligent routing every 3 minutes
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.agents.base_agent import BaseAgent
from app.models import (
    Complaint, ComplaintAssignment, ComplaintCategory,
    ProjectTeamMember, User, Project
)
from app.utils.constants import ComplaintStatus, SeverityLevel, CATEGORY_DEPARTMENT_MAP
from app.utils.helpers import calculate_sla_deadline, calculate_assignment_score, get_category_keywords
from app.services.notification_service import notification_service


class MappingAgent(BaseAgent):
    """
    Mapping Agent - Project-based intelligent routing
    Schedule: Every 3 minutes
    
    Routing Logic:
    1. If project_id exists: Score project team members and assign to best
    2. Else: Use category→department mapping, assign to lowest workload
    """
    
    async def execute(self) -> Dict[str, Any]:
        """Route categorized complaints to appropriate handlers"""
        # Find categorized complaints without assignments
        query = select(Complaint).where(
            Complaint.status == ComplaintStatus.CATEGORIZED
        ).outerjoin(
            ComplaintAssignment
        ).where(
            ComplaintAssignment.assignment_id == None
        ).options(
            selectinload(Complaint.category),
            selectinload(Complaint.project).selectinload(Project.team_members).selectinload(ProjectTeamMember.user)
        ).limit(10)
        
        if self.org_id:
            query = query.where(Complaint.org_id == self.org_id)
        
        result = await self.db.execute(query)
        complaints = result.scalars().unique().all()
        
        if not complaints:
            return {"processed": 0, "message": "No complaints to route"}
        
        assigned = 0
        for complaint in complaints:
            assignment = await self._route_complaint(complaint)
            if assignment:
                self.db.add(assignment)
                complaint.status = ComplaintStatus.IN_PROGRESS
                assigned += 1
        
        await self.db.flush()
        
        return {
            "processed": len(complaints),
            "assigned": assigned,
            "message": f"Assigned {assigned} complaints"
        }
    
    async def _route_complaint(self, complaint: Complaint) -> Optional[ComplaintAssignment]:
        """Route a single complaint using project-based or category-based logic"""
        severity = SeverityLevel.MEDIUM
        category_type = "support"
        sub_category = ""
        
        if complaint.category:
            severity = complaint.category.severity
            category_type = complaint.category.category_type
            sub_category = complaint.category.sub_category or ""
        
        assigned_user_id = None
        assignment_reason = ""
        
        # Helper to safely get severity value
        severity_val = severity.value if hasattr(severity, "value") else str(severity)
        
        # PROJECT-BASED ROUTING (Priority)
        if complaint.project_id and complaint.project:
            team_members = complaint.project.team_members
            if team_members:
                best_member, score = await self._find_best_team_member(
                    team_members, category_type, sub_category, severity_val
                )
                if best_member:
                    assigned_user_id = best_member.user_id
                    assignment_reason = f"project_member (score: {score})"
        
        # FALLBACK: Category-based routing
        if not assigned_user_id:
            department = CATEGORY_DEPARTMENT_MAP.get(category_type, "Support")
            user = await self._find_user_by_department(complaint.org_id, department)
            if user:
                assigned_user_id = user.user_id
                assignment_reason = f"category_match ({department})"
        
        if not assigned_user_id:
            return None
        
        # Calculate SLA deadline
        sla_deadline = calculate_sla_deadline(severity_val)
        
        return ComplaintAssignment(
            complaint_id=complaint.complaint_id,
            assigned_to_user_id=assigned_user_id,
            assignment_reason=assignment_reason,
            sla_deadline=sla_deadline,
            assigned_by="agent"
        )
    
    async def _find_best_team_member(
        self,
        team_members: List[ProjectTeamMember],
        category_type: str,
        sub_category: str,
        severity: str
    ) -> tuple:
        """Score team members and return best match"""
        best_member = None
        best_score = -1
        
        keywords = get_category_keywords(category_type, sub_category)
        
        for member in team_members:
            if not member.is_active:
                continue
            
            # Get current workload
            workload = member.current_workload or 0
            capacity = member.workload_capacity or 10
            
            # Calculate score
            score = calculate_assignment_score(
                role=member.role,
                specialization=member.specialization or [],
                workload=workload,
                workload_capacity=capacity,
                severity=severity,
                category_keywords=keywords
            )
            
            if score > best_score:
                best_score = score
                best_member = member
        
        return best_member, best_score
    
    async def _find_user_by_department(
        self,
        org_id: UUID,
        department_name: str
    ) -> Optional[User]:
        """Find user in department with lowest workload"""
        from app.utils.constants import UserStatus
        from app.models.department import Department
        
        # Join with Department table to match by name
        # Explicit ON clause required due to multiple FKs
        result = await self.db.execute(
            select(User).join(Department, User.department_id == Department.department_id).where(
                User.org_id == org_id,
                Department.name == department_name,
                User.status == UserStatus.ACTIVE
            ).limit(5)
        )
        users = result.scalars().all()
        
        if not users:
            # Fallback: any active user
            result = await self.db.execute(
                select(User).where(
                    User.org_id == org_id,
                    User.status == UserStatus.ACTIVE
                ).limit(1)
            )
            user = result.scalar_one_or_none()
            return user
        
        # Return first user (could enhance with workload check)
        return users[0] if users else None
