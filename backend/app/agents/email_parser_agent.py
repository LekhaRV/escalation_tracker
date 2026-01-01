"""
Tarento AI Complaint Tracking System - Email Parser Agent
Uses Redis queue for reliable email processing
"""

from typing import Dict, Any
from sqlalchemy import select

from app.agents.base_agent import BaseAgent
from app.models import Complaint, Project
from app.services.email_service import email_service
from app.services.queue_service import queue_service
from app.utils.constants import ComplaintStatus
import logging

logger = logging.getLogger(__name__)


class EmailParserAgent(BaseAgent):
    """
    Email Parser Agent - Fetches and parses complaints from email
    Now uses Redis queue for reliable processing.
    
    Two-phase approach:
    - Phase 1 (fetch_and_queue): Fetch emails → Push to Redis queue
    - Phase 2 (process_queue): Pop from queue → AI processing → Database
    """
    
    async def execute(self) -> Dict[str, Any]:
        """
        Main execution: Fetch emails to queue, then process queue.
        Can be split into separate calls for better reliability.
        """
        # Phase 1: Fetch and queue
        fetch_result = await self.fetch_and_queue()
        
        # Phase 2: Process from queue
        process_result = await self.process_queue()
        
        return {
            "fetched": fetch_result.get("fetched", 0),
            "queued": fetch_result.get("queued", 0),
            "processed": process_result.get("processed", 0),
            "created": process_result.get("created", 0),
            "failed": process_result.get("failed", 0),
            "message": f"Fetched {fetch_result.get('fetched', 0)}, processed {process_result.get('created', 0)} emails"
        }
    
    async def fetch_and_queue(self) -> Dict[str, Any]:
        """
        Phase 1: Fetch emails from IMAP and push to Redis queue.
        This is fast and ensures emails are safely stored before processing.
        """
        try:
            emails = await email_service.fetch_new_emails()
            
            if not emails:
                return {"fetched": 0, "queued": 0, "message": "No new emails"}
            
            # Push all to queue
            email_ids = await queue_service.enqueue_batch(emails)
            
            logger.info(f"Fetched {len(emails)} emails, queued {len(email_ids)}")
            
            return {
                "fetched": len(emails),
                "queued": len(email_ids),
                "email_ids": email_ids,
                "message": f"Queued {len(email_ids)} emails for processing"
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_and_queue: {str(e)}")
            return {"fetched": 0, "queued": 0, "error": str(e)}
    
    async def process_queue(self, max_items: int = 10) -> Dict[str, Any]:
        """
        Phase 2: Process emails from Redis queue.
        Processes up to max_items emails per call.
        """
        processed = 0
        created = 0
        failed = 0
        
        for _ in range(max_items):
            # Get next email from queue
            email_data = await queue_service.dequeue_email()
            
            if not email_data:
                break  # Queue is empty
            
            email_id = email_data.get("id")
            
            try:
                # Process with AI
                await email_service.process_simulated_email(
                    subject=email_data.get("subject", "No Subject"),
                    content=email_data.get("content", ""),
                    sender=email_data.get("sender", "unknown@example.com"),
                    db_session=self.db
                )
                
                # Mark as completed
                await queue_service.mark_completed(email_id)
                processed += 1
                created += 1
                
            except Exception as e:
                logger.error(f"Failed to process email {email_id}: {str(e)}")
                await queue_service.mark_failed(email_id, str(e))
                failed += 1
                continue
        
        # Get remaining queue stats
        stats = await queue_service.get_stats()
        
        return {
            "processed": processed,
            "created": created,
            "failed": failed,
            "queue_remaining": stats.get("pending", 0),
            "message": f"Processed {created} emails, {failed} failed"
        }
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue statistics"""
        stats = await queue_service.get_stats()
        preview = await queue_service.peek_queue(3)
        
        return {
            "stats": stats,
            "preview": [
                {"id": e["id"], "subject": e["subject"][:50], "sender": e["sender"]}
                for e in preview
            ]
        }
    
    async def retry_failed_emails(self) -> Dict[str, Any]:
        """Retry emails that previously failed"""
        count = await queue_service.retry_failed()
        return {"retried": count}
