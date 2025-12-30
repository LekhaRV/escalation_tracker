"""
Tarento AI Complaint Tracking System - Escalation Agent
Runs hourly to check SLA and auto-escalate
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.agents.base_agent import BaseAgent
from app.models import Complaint, ComplaintAssignment, ComplaintEscalation
from app.utils.constants import ComplaintStatus
from app.services.notification_service import notification_service


class EscalationAgent(BaseAgent):
    """
    Escalation Agent - Monitors SLA and auto-escalates
    Schedule: Every hour
    """
    
    async def execute(self) -> Dict[str, Any]:
        """Check SLA deadlines and escalate as needed"""
        now = datetime.utcnow()
        warning_threshold = now + timedelta(hours=2)
        
        # Find assignments approaching or past SLA
        query = select(ComplaintAssignment).join(
            Complaint
        ).where(
            Complaint.status.in_([ComplaintStatus.NEW, ComplaintStatus.CATEGORIZED, ComplaintStatus.IN_PROGRESS]),
            ComplaintAssignment.sla_deadline < warning_threshold
        ).options(
            selectinload(ComplaintAssignment.complaint).selectinload(Complaint.project),
            selectinload(ComplaintAssignment.assigned_user)
        ).limit(50)
        
        result = await self.db.execute(query)
        assignments = result.scalars().unique().all()
        
        if not assignments:
            return {"processed": 0, "warnings": 0, "escalations": 0}
        
        warnings = 0
        escalations = 0
        
        for assignment in assignments:
            if assignment.sla_deadline > now:
                # Warning: within 2 hours
                if assignment.assigned_user:
                    await notification_service.send_sla_warning(
                        assignment.assigned_user.email,
                        assignment.complaint.subject,
                        int((assignment.sla_deadline - now).total_seconds() / 3600)
                    )
                warnings += 1
            else:
                # Breached: auto-escalate
                await self._escalate_complaint(assignment)
                escalations += 1
        
        await self.db.flush()
        
        return {
            "processed": len(assignments),
            "warnings": warnings,
            "escalations": escalations,
            "message": f"Sent {warnings} warnings, escalated {escalations}"
        }
    
    async def _escalate_complaint(self, assignment: ComplaintAssignment):
        """Escalate a complaint that has breached SLA"""
        complaint = assignment.complaint
        
        # Determine current escalation level
        current_level = 0
        if complaint.escalations:
            current_level = max(e.escalation_level for e in complaint.escalations)
        
        new_level = min(current_level + 1, 3)
        
        # Find escalation target
        escalation_user_id = None
        if complaint.project:
            if new_level == 1:
                escalation_user_id = complaint.project.team_lead_id
            else:
                escalation_user_id = complaint.project.project_manager_id
        
        # Create escalation record
        escalation = ComplaintEscalation(
            complaint_id=complaint.complaint_id,
            escalation_level=new_level,
            escalated_to_user_id=escalation_user_id,
            escalation_reason=f"SLA breach - auto-escalated to level {new_level}",
            escalated_by="agent"
        )
        
        self.db.add(escalation)
