"""
Tarento AI Complaint Tracking System - Analytics Service
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import (
    Complaint, ComplaintCategory, ComplaintAssignment,
    ComplaintPattern, ComplaintInsight, Project
)
from app.utils.constants import ComplaintStatus, SeverityLevel


class AnalyticsService:
    """Analytics and reporting service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_stats(self, org_id: UUID) -> Dict[str, Any]:
        """Get dashboard statistics"""
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Total counts by status
        total = await self._count_complaints(org_id)
        new = await self._count_complaints(org_id, ComplaintStatus.NEW)
        in_progress = await self._count_complaints(org_id, ComplaintStatus.IN_PROGRESS)
        resolved = await self._count_complaints(org_id, ComplaintStatus.RESOLVED)
        
        # By severity
        critical = await self._count_by_severity(org_id, SeverityLevel.CRITICAL)
        high = await self._count_by_severity(org_id, SeverityLevel.HIGH)
        medium = await self._count_by_severity(org_id, SeverityLevel.MEDIUM)
        low = await self._count_by_severity(org_id, SeverityLevel.LOW)
        
        # Time-based
        today_count = await self._count_since(org_id, today)
        week_count = await self._count_since(org_id, week_ago)
        month_count = await self._count_since(org_id, month_ago)
        
        # SLA
        overdue = await self._count_overdue(org_id)
        compliance = 100 - (overdue / max(total, 1) * 100)
        
        # Daily trends
        trends = await self.get_daily_trends(org_id)
        
        # Recent patterns & insights
        patterns = await self.get_patterns(org_id)
        insights = await self.get_insights(org_id)
        
        return {
            "total_complaints": total,
            "new_complaints": new,
            "in_progress_complaints": in_progress,
            "resolved_complaints": resolved,
            "sla_compliance_rate": round(compliance, 1),
            "overdue_complaints": overdue,
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "complaints_today": today_count,
            "complaints_this_week": week_count,
            "complaints_this_month": month_count,
            "avg_resolution_time_hours": 24.0,
            "resolution_rate": round(resolved / max(total, 1) * 100, 1),
            "daily_trends": trends,
            "recent_patterns": patterns,
            "recent_insights": insights
        }
    
    async def get_daily_trends(self, org_id: UUID, days: int = 7) -> List[Dict[str, Any]]:
        """Get complaint counts for the last N days"""
        trends = []
        now = datetime.utcnow()
        
        for i in range(days - 1, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_name = day_start.strftime("%a") # Mon, Tue
            
            # Count complaints created on this day
            query = select(func.count()).select_from(Complaint).where(
                Complaint.org_id == org_id,
                Complaint.created_at >= day_start,
                Complaint.created_at < day_end
            )
            result = await self.db.execute(query)
            count = result.scalar() or 0
            
            trends.append({
                "name": day_name,
                "date": day_start.strftime("%Y-%m-%d"),
                "complaints": count
            })
            
        return trends

    async def _count_complaints(
        self,
        org_id: UUID,
        status: Optional[ComplaintStatus] = None
    ) -> int:
        query = select(func.count()).select_from(Complaint).where(
            Complaint.org_id == org_id
        )
        if status:
            query = query.where(Complaint.status == status)
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _count_by_severity(self, org_id: UUID, severity: SeverityLevel) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Complaint).join(
                ComplaintCategory
            ).where(
                Complaint.org_id == org_id,
                ComplaintCategory.severity == severity
            )
        )
        return result.scalar() or 0
    
    async def _count_since(self, org_id: UUID, since: datetime) -> int:
        result = await self.db.execute(
            select(func.count()).where(
                Complaint.org_id == org_id,
                Complaint.created_at >= since
            )
        )
        return result.scalar() or 0
    
    async def _count_overdue(self, org_id: UUID) -> int:
        now = datetime.utcnow()
        result = await self.db.execute(
            select(func.count()).select_from(Complaint).join(
                ComplaintAssignment
            ).where(
                Complaint.org_id == org_id,
                Complaint.status.in_([ComplaintStatus.NEW, ComplaintStatus.IN_PROGRESS]),
                ComplaintAssignment.sla_deadline < now
            )
        )
        return result.scalar() or 0
    
    async def get_patterns(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get active patterns"""
        result = await self.db.execute(
            select(ComplaintPattern).where(
                ComplaintPattern.org_id == org_id
            ).order_by(ComplaintPattern.detected_at.desc()).limit(5)
        )
        patterns = result.scalars().all()
        return [{
            "pattern_id": str(p.pattern_id), 
            "type": p.pattern_type.value,
            "description": p.pattern_description,
            "detected_at": p.detected_at.isoformat() if p.detected_at else None,
            "confidence": float(p.severity_score or 0)
        } for p in patterns]
    
    async def get_insights(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get recent insights"""
        from app.utils.constants import InsightType
        
        # If no insights exist, generate placeholder ones for demo
        result = await self.db.execute(
            select(ComplaintInsight).where(
                ComplaintInsight.org_id == org_id
            ).order_by(ComplaintInsight.generated_at.desc()).limit(5)
        )
        insights = result.scalars().all()
        
        if not insights:
            # Return some safe defaults if system is fresh
            return []
            
        return [{
            "insight_id": str(i.insight_id), 
            "type": i.insight_type.value,
            "title": i.title,
            "description": i.description,
            "generated_at": i.generated_at.isoformat()
        } for i in insights]
