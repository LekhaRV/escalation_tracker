"""
Tarento AI Complaint Tracking System - Insight Generation Agent
Runs weekly on Sunday at 3 AM
"""

from typing import Dict, Any
from sqlalchemy import select, func

from app.agents.base_agent import BaseAgent
from app.models import Complaint, ComplaintCategory, ComplaintInsight
from app.services.gemini_service import gemini_service
from app.utils.constants import InsightType, ImpactLevel, ComplaintStatus


class InsightAgent(BaseAgent):
    """
    Insight Generation Agent - Creates executive insights
    Schedule: Weekly Sunday at 3 AM
    """
    
    async def execute(self) -> Dict[str, Any]:
        """Generate executive insights from analytics"""
        # Gather analytics data
        analytics = await self._gather_analytics()
        
        # Use Gemini to generate insights
        insights_data = await gemini_service.generate_insights(analytics)
        
        created = 0
        for insight_data in insights_data.get("insights", []):
            insight = ComplaintInsight(
                org_id=self.org_id,
                insight_type=InsightType(insight_data.get("insight_type", "recommendation")),
                title=insight_data.get("title", "Insight"),
                description=insight_data.get("description"),
                related_patterns=[],
                related_projects=[],
                impact_level=ImpactLevel(insight_data.get("impact_level", "medium")),
                actionable=insight_data.get("actionable", True)
            )
            self.db.add(insight)
            created += 1
        
        await self.db.flush()
        
        return {
            "insights_created": created,
            "executive_summary": insights_data.get("executive_summary", ""),
            "message": f"Generated {created} insights"
        }
    
    async def _gather_analytics(self) -> Dict[str, Any]:
        """Gather analytics data for insight generation"""
        # Total complaints
        total_query = select(func.count()).select_from(Complaint)
        if self.org_id:
            total_query = total_query.where(Complaint.org_id == self.org_id)
        total = (await self.db.execute(total_query)).scalar() or 0
        
        # By category
        by_category = {}
        cat_result = await self.db.execute(
            select(ComplaintCategory.category_type, func.count()).group_by(
                ComplaintCategory.category_type
            )
        )
        for row in cat_result:
            by_category[row[0]] = row[1]
        
        # Resolution stats
        resolved = await self.db.execute(
            select(func.count()).where(
                Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
            )
        )
        resolved_count = resolved.scalar() or 0
        
        return {
            "total_complaints": total,
            "by_category": by_category,
            "by_project": {},
            "avg_resolution_hours": 24,
            "sla_compliance": round((resolved_count / max(total, 1)) * 100, 1)
        }
