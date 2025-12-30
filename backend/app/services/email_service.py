"""
Tarento AI Complaint Tracking System - Email Service
IMAP email ingestion
"""

from typing import Optional, List, Dict, Any
from app.config import settings
from app.core.logging import logger


class EmailService:
    """Service for email ingestion via IMAP"""
    
    def __init__(self):
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USERNAME
        self.password = settings.EMAIL_PASSWORD
    
    async def fetch_new_emails(self) -> List[Dict[str, Any]]:
        """Fetch new unread emails from IMAP server"""
        if not self.username or not self.password:
            logger.warning("Email credentials not configured")
            return []
        
        # Placeholder - actual IMAP implementation
        logger.info("Email fetch not fully implemented")
        return []
    
    def match_project_from_email(
        self,
        customer_email: str,
        subject: str,
        projects: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Match email to a project based on domain or subject"""
        if not projects:
            return None
        
        domain = customer_email.split("@")[1].lower() if "@" in customer_email else ""
        subject_lower = subject.lower()
        
        for project in projects:
            if project.get("project_code") and project["project_code"].lower() in subject_lower:
                return project["project_id"]
            if project.get("client_name") and domain:
                if project["client_name"].lower().replace(" ", "") in domain:
                    return project["project_id"]
        
        return None


email_service = EmailService()
