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
            
        import imaplib
        import email
        from email.header import decode_header

        emails = []
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.host)
            mail.login(self.username, self.password)
            mail.select("inbox")
            
            # Search for unread emails
            status, messages = mail.search(None, "UNSEEN")
            if status != "OK" or not messages[0]:
                mail.logout()
                return []
                
            email_ids = messages[0].split()
            
            for e_id in email_ids:
                try:
                    # Fetch header and body
                    _, msg_data = mail.fetch(e_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Decode subject
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8")
                            
                            # Get Sender
                            sender = msg.get("From")
                            
                            # Get Body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode()
                                        break
                            else:
                                body = msg.get_payload(decode=True).decode()
                                
                            emails.append({
                                "subject": subject,
                                "sender": sender,
                                "content": body,
                                "raw_data": str(msg)
                            })
                            
                except Exception as e:
                    logger.error(f"Error parsing email {e_id}: {str(e)}")
                    continue
            
            mail.close()
            mail.logout()
            logger.info(f"Fetched {len(emails)} new emails")
            return emails
            
        except Exception as e:
            logger.error(f"IMAP connection failed: {str(e)}")
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
        
        # 1. Project Code Match
        for project in projects:
            if project.get("project_code") and project["project_code"].lower() in subject_lower:
                return project["project_id"]
        
        # 2. Domain Match (Robost)
        if domain:
            for project in projects:
                client_name = project.get("client_name", "").lower()
                clean_client = client_name.replace(" ", "")
                # Match "globalbank" in "globalbank.com"
                if clean_client and clean_client in domain:
                    return project["project_id"]
                # Match "global" in "globalbank.com" (first word fallback)
                first_word = client_name.split(" ")[0]
                if first_word and len(first_word) > 3 and first_word in domain:
                    return project["project_id"]
        
        return None

    async def process_simulated_email(self, subject: str, content: str, sender: str, db_session) -> Dict[str, Any]:
        """
        Manually inject an email into the system for processing (Simulation/Debug)
        Triggering the entire AI pipeline:
        1. Categorize (Agent)
        2. Create Complaint
        3. Match Project (Agent)
        4. Assign (Agent)
        """
        from app.services.complaint_service import ComplaintService
        from app.services.gemini_service import gemini_service
        from app.services.complaint_service import ComplaintService
        from app.services.gemini_service import gemini_service
        from app.utils.constants import ComplaintStatus, SeverityLevel
        from app.schemas.complaint import ComplaintCreate
        from app.models.complaint import Complaint
        from app.schemas.complaint import ComplaintCreate
        
        logger.info(f"Processing simulated email from {sender}: {subject}")
        
        # 1. AI Categorization
        categorization = await gemini_service.categorize_complaint(subject, content)
        
        # FILTER: If AI determines this is not a complaint, skip it
        if categorization.get("is_complaint") is False:
            logger.info("AI determined this email is NOT a complaint. Skipping.")
            return {
                "status": "ignored",
                "reason": "Not a complaint",
                "category": "ignored"
            }
        # Parse sender email properly (handle "Name" <email@domain.com> format)
        import re
        email_match = re.search(r'<(.+?)>', sender)
        if email_match:
            parsed_email = email_match.group(1)
            # Name is everything before the angle bracket
            name_part = re.sub(r'<.*>', '', sender).strip().strip('"').strip("'")
            parsed_name = name_part if name_part else parsed_email.split('@')[0].replace('.', ' ').title()
        else:
            # Plain email without display name
            parsed_email = sender
            parsed_name = sender.split('@')[0].replace('.', ' ').title()
        
        # 2. Create basic complaint
        complaint_in = ComplaintCreate(
            subject=subject,
            description=content,
            customer_email=parsed_email,
            customer_name=parsed_name,
            priority=categorization.get("severity", "medium").lower(),
            # Status defaults to NEW
        )
        
        complaint_service = ComplaintService(db_session)
        # We need an org_id context. For simulation, we'll pick the first available org or a default.
        # Ideally this comes from the user context but email allows exogenous input.
        # We'll fetch the default org ID from the DB.
        from sqlalchemy import select
        from app.models.organization import Organization
        
        org_result = await db_session.execute(select(Organization))
        default_org = org_result.scalars().first()
        
        if not default_org:
            raise Exception("No organization found to attach simulated complaint to")
            
        complaint = await complaint_service.create_complaint(default_org.org_id, complaint_in)
        
        
        # 3. Create AI Category record
        from app.models.complaint_category import ComplaintCategory
        
        category_data = ComplaintCategory(
            complaint_id=complaint.complaint_id,
            category_type=categorization.get("category_type", "support"),
            sub_category=categorization.get("sub_category", "general"),
            severity=categorization.get("severity", "medium").lower(),
            priority=categorization.get("priority", 3),
            department=categorization.get("department", "Support"),
            confidence_score=categorization.get("confidence_score", 0.8),
            categorized_by="ai_agent"
        )
        db_session.add(category_data)
        complaint.status = ComplaintStatus.CATEGORIZED
        await db_session.flush()
        
        # 4. Project Matching
        from app.models.project import Project
        from sqlalchemy import select
        
        project_id = None
        projects_data = []
        
        # Fetch projects for matching
        p_result = await db_session.execute(select(Project).where(Project.org_id == default_org.org_id))
        db_projects = p_result.scalars().all()
        
        projects_data = [
            {
                "project_id": str(p.project_id),
                "project_code": p.project_code,
                "project_name": p.project_name,
                "client_name": p.client_name
            }
            for p in db_projects
        ]
        
        # Try Deterministic Match First (Fast)
        project_id = self.match_project_from_email(sender, subject, projects_data)
        match_source = "Deterministic"

        # Fallback to AI Match (Smart)
        if not project_id:
            logger.info("Deterministic project match failed. Trying AI matching...")
            try:
                project_id = await gemini_service.match_project(subject, content, projects_data)
                if project_id:
                    match_source = "AI Semantic Match"
            except Exception as e:
                logger.error(f"AI Project matching failed: {e}")
        
        if project_id:
            logger.info(f"Simulated email matched to project {project_id} (Source: {match_source})")
            complaint_in.project_id = project_id
            # Update the preliminary complaint with the project ID
            complaint.project_id = project_id
            db_session.add(complaint)
            await db_session.flush()
        
        # Refresh to load relationships for agents
        from sqlalchemy.orm import selectinload
        from app.models.project import Project
        from app.models.project_team_member import ProjectTeamMember
        
        refresh_query = select(Complaint).where(
            Complaint.complaint_id == complaint.complaint_id
        ).options(
            selectinload(Complaint.category),
            selectinload(Complaint.project).selectinload(Project.team_members).selectinload(ProjectTeamMember.user)
        )
        refresh_result = await db_session.execute(refresh_query)
        complaint = refresh_result.scalar_one()
        
        # 4. Trigger AI Assignment (Mapping Agent)
        from app.agents.mapping_agent import MappingAgent
        
        mapping_agent = MappingAgent(db_session, default_org.org_id)
        assignment = await mapping_agent._route_complaint(complaint)
        
        if assignment:
            logger.info(f"Simulated complaint assigned to user {assignment.assigned_to_user_id}")
            db_session.add(assignment)
            complaint.status = ComplaintStatus.IN_PROGRESS
            await db_session.flush()

        return {
            "status": "processed",
            "complaint_id": complaint.complaint_id,
            "project_matched": bool(project_id),
            "assigned": bool(assignment),
            "severity": categorization.get("severity", "medium"),
            "category": categorization.get("category_type", "support")
        }


email_service = EmailService()
