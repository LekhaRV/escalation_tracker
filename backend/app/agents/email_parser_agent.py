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
        
        
        processed_count = 0
        for email_data in emails:
            try:
                # Use the existing processing logic (same as simulation) to ensure
                # AI categorization, project matching, and assignment all happen.
                await email_service.process_simulated_email(
                    subject=email_data.get("subject", "No Subject"),
                    content=email_data.get("content", ""),
                    sender=email_data.get("sender", "unknown@example.com"),
                    db_session=self.db
                )
                processed_count += 1
            except Exception as e:
                # Log error but continue processing other emails
                from app.core.logging import logger
                logger.error(f"Failed to process email from {email_data.get('sender')}: {str(e)}")
                continue
            
        return {
            "processed": len(emails),
            "created": processed_count,
            "message": f"Successfully processed {processed_count} emails"
        }
        
        await self.db.flush()
        
        return {
            "processed": len(emails),
            "created": created,
            "message": f"Created {created} complaints from {len(emails)} emails"
        }
