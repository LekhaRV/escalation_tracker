"""
Tarento AI Complaint Tracking System - Pattern Detection Agent
Runs daily at 2 AM to detect patterns
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.agents.base_agent import BaseAgent
from app.models import Complaint, ComplaintPattern, ComplaintCategory
from app.services.gemini_service import gemini_service
from app.utils.constants import PatternType, PatternStatus


class PatternAgent(BaseAgent):
    """
    Pattern Detection Agent - Identifies recurring issues
    Schedule: Daily at 2 AM
    """
    
    async def execute(self) -> Dict[str, Any]:
        """Analyze complaints for patterns"""
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        # Get complaints from last 30 days
        query = select(Complaint).where(
            Complaint.created_at >= cutoff
        ).options(
            selectinload(Complaint.category),
            selectinload(Complaint.project)
        )
        
        if self.org_id:
            query = query.where(Complaint.org_id == self.org_id)
        
        result = await self.db.execute(query)
        complaints = result.scalars().unique().all()
        
        if len(complaints) < 5:
            return {"processed": 0, "patterns": 0, "message": "Not enough data"}
        
        # Prepare data for analysis
        complaints_data = [
            {
                "id": str(c.complaint_id),
                "category": c.category.category_type if c.category else "unknown",
                "subject": c.subject,
                "project": c.project.project_name if c.project else None
            }
            for c in complaints
        ]
        
        # Use Gemini to detect patterns
        patterns = await gemini_service.detect_patterns(complaints_data)
        
        created = 0
        for pattern_data in patterns:
            pattern = ComplaintPattern(
                org_id=self.org_id,
                pattern_type=PatternType(pattern_data.get("pattern_type", "recurring")),
                pattern_description=pattern_data.get("description"),
                affected_complaints=pattern_data.get("affected_ids", []),
                affected_projects=[],
                frequency=pattern_data.get("frequency", 1),
                severity_score=pattern_data.get("severity_score", 0.5),
                status=PatternStatus.ACTIVE
            )
            self.db.add(pattern)
            created += 1
        
        await self.db.flush()
        
        return {
            "processed": len(complaints),
            "patterns": created,
            "message": f"Detected {created} patterns from {len(complaints)} complaints"
        }
