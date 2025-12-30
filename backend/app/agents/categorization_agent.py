"""
Tarento AI Complaint Tracking System - Categorization Agent
Runs every 2 minutes to categorize new complaints using AI
"""

from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.agents.base_agent import BaseAgent
from app.models import Complaint, ComplaintCategory
from app.services.gemini_service import gemini_service
from app.utils.constants import ComplaintStatus, SeverityLevel


class CategorizationAgent(BaseAgent):
    """
    Categorization Agent - Uses Gemini AI to categorize complaints
    Schedule: Every 2 minutes
    """
    
    async def execute(self) -> Dict[str, Any]:
        """Categorize uncategorized complaints"""
        # Find complaints without categories
        query = select(Complaint).where(
            Complaint.status == ComplaintStatus.NEW
        ).outerjoin(
            ComplaintCategory
        ).where(
            ComplaintCategory.category_id == None
        ).options(
            selectinload(Complaint.project)
        ).limit(10)
        
        if self.org_id:
            query = query.where(Complaint.org_id == self.org_id)
        
        result = await self.db.execute(query)
        complaints = result.scalars().unique().all()
        
        if not complaints:
            return {"processed": 0, "message": "No complaints to categorize"}
        
        categorized = 0
        for complaint in complaints:
            # Get project info
            project_name = complaint.project.project_name if complaint.project else None
            client_name = complaint.project.client_name if complaint.project else None
            
            # Call Gemini for categorization
            cat_result = await gemini_service.categorize_complaint(
                subject=complaint.subject,
                description=complaint.description or "",
                project_name=project_name,
                client_name=client_name
            )
            
            # Create category record
            category = ComplaintCategory(
                complaint_id=complaint.complaint_id,
                category_type=cat_result.get("category_type", "support"),
                sub_category=cat_result.get("sub_category"),
                severity=SeverityLevel(cat_result.get("severity", "medium")),
                priority=cat_result.get("priority", 3),
                department=cat_result.get("department"),
                confidence_score=cat_result.get("confidence_score", 0.5),
                categorized_by="agent"
            )
            
            self.db.add(category)
            
            # Update complaint status
            complaint.status = ComplaintStatus.CATEGORIZED
            categorized += 1
        
        await self.db.flush()
        
        return {
            "processed": len(complaints),
            "categorized": categorized,
            "message": f"Categorized {categorized} complaints"
        }
