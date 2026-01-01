"""
Tarento AI Complaint Tracking System - Redis Queue Service
Persistent email queue for reliable processing
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class QueueService:
    """Redis-based queue for email processing"""
    
    QUEUE_NAME = "email:pending"
    PROCESSING_QUEUE = "email:processing"
    FAILED_QUEUE = "email:failed"
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        if self.redis is None:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379/0')
            self.redis = redis.from_url(redis_url, decode_responses=True)
            logger.info(f"Connected to Redis at {redis_url}")
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    async def enqueue_email(self, email_data: Dict[str, Any]) -> str:
        """
        Add email to the processing queue.
        Returns the email ID for tracking.
        """
        await self.connect()
        
        email_id = str(uuid.uuid4())
        queue_item = {
            "id": email_id,
            "subject": email_data.get("subject", ""),
            "sender": email_data.get("sender", ""),
            "content": email_data.get("content", ""),
            "raw_data": email_data.get("raw_data", ""),
            "fetched_at": datetime.utcnow().isoformat(),
            "attempts": 0
        }
        
        # Push to queue
        await self.redis.lpush(self.QUEUE_NAME, json.dumps(queue_item))
        logger.info(f"Enqueued email {email_id}: {queue_item['subject'][:50]}...")
        
        return email_id
    
    async def enqueue_batch(self, emails: List[Dict[str, Any]]) -> List[str]:
        """Enqueue multiple emails at once"""
        email_ids = []
        for email in emails:
            email_id = await self.enqueue_email(email)
            email_ids.append(email_id)
        return email_ids
    
    async def dequeue_email(self) -> Optional[Dict[str, Any]]:
        """
        Get next email from queue for processing.
        Moves to processing queue until confirmed done.
        """
        await self.connect()
        
        # Atomically move from pending to processing
        item = await self.redis.rpoplpush(self.QUEUE_NAME, self.PROCESSING_QUEUE)
        
        if item:
            data = json.loads(item)
            data["attempts"] += 1
            data["started_at"] = datetime.utcnow().isoformat()
            
            # Update in processing queue
            await self.redis.lrem(self.PROCESSING_QUEUE, 1, item)
            await self.redis.lpush(self.PROCESSING_QUEUE, json.dumps(data))
            
            logger.info(f"Dequeued email {data['id']} (attempt {data['attempts']})")
            return data
        
        return None
    
    async def mark_completed(self, email_id: str):
        """Remove email from processing queue after successful processing"""
        await self.connect()
        
        # Find and remove from processing queue
        items = await self.redis.lrange(self.PROCESSING_QUEUE, 0, -1)
        for item in items:
            data = json.loads(item)
            if data.get("id") == email_id:
                await self.redis.lrem(self.PROCESSING_QUEUE, 1, item)
                logger.info(f"Completed processing email {email_id}")
                return True
        return False
    
    async def mark_failed(self, email_id: str, error: str):
        """Move email to failed queue"""
        await self.connect()
        
        # Find in processing queue
        items = await self.redis.lrange(self.PROCESSING_QUEUE, 0, -1)
        for item in items:
            data = json.loads(item)
            if data.get("id") == email_id:
                await self.redis.lrem(self.PROCESSING_QUEUE, 1, item)
                
                # Add error info and move to failed
                data["error"] = error
                data["failed_at"] = datetime.utcnow().isoformat()
                await self.redis.lpush(self.FAILED_QUEUE, json.dumps(data))
                
                logger.warning(f"Email {email_id} failed: {error}")
                return True
        return False
    
    async def retry_failed(self) -> int:
        """Move failed emails back to pending queue for retry"""
        await self.connect()
        
        count = 0
        while True:
            item = await self.redis.rpop(self.FAILED_QUEUE)
            if not item:
                break
            
            data = json.loads(item)
            if data.get("attempts", 0) < 3:  # Max 3 retries
                data["error"] = None
                data["failed_at"] = None
                await self.redis.lpush(self.QUEUE_NAME, json.dumps(data))
                count += 1
            else:
                # Permanently failed - could log or alert
                logger.error(f"Email {data['id']} permanently failed after 3 attempts")
        
        return count
    
    async def get_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        await self.connect()
        
        return {
            "pending": await self.redis.llen(self.QUEUE_NAME),
            "processing": await self.redis.llen(self.PROCESSING_QUEUE),
            "failed": await self.redis.llen(self.FAILED_QUEUE)
        }
    
    async def peek_queue(self, count: int = 5) -> List[Dict[str, Any]]:
        """Preview items in queue without removing them"""
        await self.connect()
        
        items = await self.redis.lrange(self.QUEUE_NAME, -count, -1)
        return [json.loads(item) for item in items]


# Singleton instance
queue_service = QueueService()
