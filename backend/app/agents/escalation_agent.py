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
    SLA Monitor Agent (formerly Escalation Agent)
    Monitors SLA deadlines and sends warnings 7 days before breach.
    Does NOT auto-escalate.
    """
    
    async def execute(self) -> Dict[str, Any]:
        """Check SLA deadlines and send warnings"""
        now = datetime.utcnow()
        # Warn if deadline is within 7 days
        warning_threshold = now + timedelta(days=7)
        
        # Find assignments approaching deadline (or recently breached)
        # We only care about active complaints
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
            return {"processed": 0, "warnings": 0, "overdue": 0}
        
        warnings = 0
        overdue = 0
        
        for assignment in assignments:
            days_left = (assignment.sla_deadline - now).total_seconds() / (24 * 3600)
            
            if assignment.sla_deadline > now:
                # Approaching Deadline (0 to 7 days left)
                if assignment.assigned_user:
                    # Send warning via notification service
                    await notification_service.send_sla_warning(
                        assignment.assigned_user.email,
                        assignment.complaint.subject,
                        int(days_left * 24) # passing hours for consistency with service signature
                    )
                warnings += 1
            else:
                # Already Overdue
                # User requested NO auto-escalation.
                # Just track stats.
                overdue += 1
        
        return {
            "processed": len(assignments),
            "warnings": warnings,
            "overdue_tracked": overdue,
            "message": f"Sent {warnings} warnings, found {overdue} overdue items (no escalation)"
        }
