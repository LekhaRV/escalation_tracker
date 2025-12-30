"""
Tarento AI Complaint Tracking System - Email Parser Agent
Runs every 5 minutes to fetch and parse emails
"""

from typing import Dict, Any
from sqlalchemy import select

from app.agents.base_agent import BaseAgent
from app.models import Complaint, Project
from app.services.email_service import email_service
from app.utils.constants import ComplaintStatus


class EmailParserAgent(BaseAgent):
    """
    Email Parser Agent - Fetches and parses complaints from email
    Schedule: Every 5 minutes
    """
    
    async def execute(self) -> Dict[str, Any]:
        """Fetch emails and create complaints"""
        # Fetch emails from IMAP
        emails = await email_service.fetch_new_emails()
        
        if not emails:
            return {"processed": 0, "message": "No new emails"}
        
        # Get projects for matching
        projects = []
        if self.org_id:
            result = await self.db.execute(
                select(Project).where(Project.org_id == self.org_id)
            )
            projects = [
                {
                    "project_id": str(p.project_id),
                    "project_code": p.project_code,
                    "project_name": p.project_name,
                    "client_name": p.client_name
                }
                for p in result.scalars().all()
            ]
        
        created = 0
        for email_data in emails:
            # Try to match to a project
            project_id = email_service.match_project_from_email(
                email_data.get("customer_email", ""),
                email_data.get("subject", ""),
                projects
            )
            
            # Create complaint
            complaint = Complaint(
                org_id=self.org_id,
                project_id=project_id,
                email_id=email_data.get("email_id"),
                customer_name=email_data.get("customer_name"),
                customer_email=email_data.get("customer_email"),
                subject=email_data.get("subject"),
                description=email_data.get("description"),
                raw_email_content=email_data.get("raw_content"),
                status=ComplaintStatus.NEW
            )
            
            self.db.add(complaint)
            created += 1
        
        await self.db.flush()
        
        return {
            "processed": len(emails),
            "created": created,
            "message": f"Created {created} complaints from {len(emails)} emails"
        }
