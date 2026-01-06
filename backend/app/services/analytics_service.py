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
from app.utils.constants import ComplaintStatus, SeverityLevel, UserRole, UserStatus


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
            "confidence": float(p.severity_score or 0),
            "affected_complaints": p.affected_complaints or []
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
    
    async def get_workload_stats(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get team workload statistics - Dynamic Calculation"""
        from app.models import User, ComplaintAssignment
        
        # 1. Get active complaint counts per user
        # We perform a left join from User -> Assignment -> Complaint
        # And filter for active complaints only
        count_query = select(
            User.user_id,
            User.name,
            User.email,
            func.count(Complaint.complaint_id).label('active_count')
        ).select_from(User).outerjoin(
            ComplaintAssignment, User.user_id == ComplaintAssignment.assigned_to_user_id
        ).outerjoin(
            Complaint, (ComplaintAssignment.complaint_id == Complaint.complaint_id) & 
                       (Complaint.status.in_([ComplaintStatus.NEW, ComplaintStatus.IN_PROGRESS]))
        ).where(
            User.org_id == org_id,
            User.role.in_([UserRole.AGENT, UserRole.ADMIN, UserRole.MANAGER]),
            User.status == UserStatus.ACTIVE
        ).group_by(
            User.user_id, User.name, User.email
        )
        
        result = await self.db.execute(count_query)
        rows = result.all()
        
        # 2. Build response (Capacity hardcoded to 10 for now as dynamic capacity is complex)
        # In a real app, we would join ProjectTeamMember for capacity, but this ensures robustness.
        stats = []
        for r in rows:
            capacity = 10 
            current = r.active_count
            utilization = min(100, round((current / capacity) * 100))
            
            stats.append({
                "user_id": str(r.user_id),
                "name": r.name,
                "email": r.email,
                "current_workload": current,
                "capacity": capacity,
                "utilization": utilization
            })
            
        # Sort by utilization desc
        stats.sort(key=lambda x: x["utilization"], reverse=True)
        return stats
    
    async def get_resolution_analytics(self, org_id: UUID) -> Dict[str, Any]:
        """Get resolution time analytics"""
        # Get resolved complaints with time to resolve
        result = await self.db.execute(
            select(
                Complaint.resolved_at,
                Complaint.created_at,
                ComplaintCategory.category_type
            ).outerjoin(
                ComplaintCategory
            ).where(
                Complaint.org_id == org_id,
                Complaint.status == ComplaintStatus.RESOLVED,
                Complaint.resolved_at.isnot(None)
            ).order_by(Complaint.resolved_at.desc()).limit(100)
        )
        
        rows = result.all()
        
        if not rows:
            return {
                "avg_resolution_hours": 0,
                "total_resolved": 0,
                "by_category": {},
                "trend": "no_data"
            }
        
        # Calculate average resolution time
        total_hours = 0
        by_category = {}
        
        for r in rows:
            if r.resolved_at and r.created_at:
                hours = (r.resolved_at - r.created_at).total_seconds() / 3600
                total_hours += hours
                
                cat = r.category_type or "uncategorized"
                if cat not in by_category:
                    by_category[cat] = {"total_hours": 0, "count": 0}
                by_category[cat]["total_hours"] += hours
                by_category[cat]["count"] += 1
        
        avg_hours = total_hours / len(rows) if rows else 0
        
        # Calculate averages per category
        for cat in by_category:
            by_category[cat]["avg_hours"] = round(
                by_category[cat]["total_hours"] / by_category[cat]["count"], 1
            )
        
        return {
            "avg_resolution_hours": round(avg_hours, 1),
            "avg_resolution_days": round(avg_hours / 24, 1),
            "total_resolved": len(rows),
            "by_category": by_category,
            "within_sla": len([r for r in rows if r.resolved_at and r.created_at and 
                             (r.resolved_at - r.created_at).days <= 60])
        }
    
    async def get_projects_in_escalation(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get projects with critical/overdue complaints for escalation dashboard"""
        from app.models import ComplaintAssignment
        
        now = datetime.utcnow()
        
        # Get projects with open complaints
        query = select(
            Project.project_id,
            Project.project_name,
            Project.client_name,
            func.count(Complaint.complaint_id).label('total_open')
        ).select_from(Project).join(
            Complaint, Complaint.project_id == Project.project_id
        ).where(
            Project.org_id == org_id,
            Complaint.status != ComplaintStatus.RESOLVED
        ).group_by(
            Project.project_id, Project.project_name, Project.client_name
        )
        
        result = await self.db.execute(query)
        projects_data = result.all()
        
        escalated_projects = []
        for row in projects_data:
            # Get critical/high counts for this project
            severity_query = select(
                func.count(Complaint.complaint_id)
            ).select_from(Complaint).join(
                ComplaintCategory, ComplaintCategory.complaint_id == Complaint.complaint_id
            ).where(
                Complaint.project_id == row.project_id,
                Complaint.status != ComplaintStatus.RESOLVED,
                ComplaintCategory.severity.in_([SeverityLevel.CRITICAL, SeverityLevel.HIGH])
            )
            sev_result = await self.db.execute(severity_query)
            critical_high = sev_result.scalar() or 0
            
            # Get overdue count
            overdue_query = select(
                func.count(Complaint.complaint_id)
            ).select_from(Complaint).join(
                ComplaintAssignment, ComplaintAssignment.complaint_id == Complaint.complaint_id
            ).where(
                Complaint.project_id == row.project_id,
                Complaint.status.in_([ComplaintStatus.NEW, ComplaintStatus.IN_PROGRESS]),
                ComplaintAssignment.sla_deadline < now
            )
            overdue_result = await self.db.execute(overdue_query)
            overdue = overdue_result.scalar() or 0
            
            if critical_high > 0 or overdue > 0:
                escalated_projects.append({
                    "project_id": str(row.project_id),
                    "project_name": row.project_name,
                    "client_name": row.client_name,
                    "critical_high_count": critical_high,
                    "overdue_count": overdue,
                    "total_open": row.total_open or 0,
                    "escalation_score": (critical_high * 2) + overdue
                })
        
        # Sort by escalation score descending
        escalated_projects.sort(key=lambda x: x["escalation_score"], reverse=True)
        
        return escalated_projects

    async def get_smart_insights(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Generate intelligent insights based on data analysis"""
        from app.models import User
        from app.utils.constants import UserRole
        
        insights = []
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 1. TREND PREDICTION: Compare this week vs last week
        this_week_start = today - timedelta(days=today.weekday())
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start
        
        this_week_count = await self._count_since(org_id, this_week_start)
        
        # Count last week
        last_week_query = select(func.count()).select_from(Complaint).where(
            Complaint.org_id == org_id,
            Complaint.created_at >= last_week_start,
            Complaint.created_at < last_week_end
        )
        result = await self.db.execute(last_week_query)
        last_week_count = result.scalar() or 0
        
        if last_week_count > 0:
            growth_rate = ((this_week_count - last_week_count) / last_week_count) * 100
            if growth_rate > 20:
                predicted = round(this_week_count * 1.2)
                insights.append({
                    "type": "trend",
                    "priority": 2,
                    "title": f"Complaint Volume Rising ({round(growth_rate)}% increase)",
                    "description": f"This week: {this_week_count} vs last week: {last_week_count}. Expect ~{predicted} by week end if trend continues.",
                    "action": "Review Queue",
                    "actionUrl": "/complaints"
                })
            elif growth_rate < -20:
                insights.append({
                    "type": "success",
                    "priority": 4,
                    "title": f"Complaint Volume Decreasing ({abs(round(growth_rate))}% drop)",
                    "description": f"Good news! This week: {this_week_count} vs last week: {last_week_count}. Improvements are working.",
                    "action": None,
                    "actionUrl": None
                })
        
        # 2. SMART ASSIGNMENT: Find top performers by category
        # Get agents with highest resolution rates
        from sqlalchemy import case
        agent_query = select(
            ComplaintAssignment.assigned_to_user_id,
            User.name,
            func.count(ComplaintAssignment.assignment_id).label('total_assigned'),
            func.count(
                case((Complaint.status == ComplaintStatus.RESOLVED, 1))
            ).label('resolved_count')
        ).select_from(ComplaintAssignment).join(
            Complaint, Complaint.complaint_id == ComplaintAssignment.complaint_id
        ).join(
            User, User.user_id == ComplaintAssignment.assigned_to_user_id
        ).where(
            Complaint.org_id == org_id,
            User.role == UserRole.AGENT
        ).group_by(
            ComplaintAssignment.assigned_to_user_id, User.name
        ).having(func.count(ComplaintAssignment.assignment_id) >= 3)
        
        agent_result = await self.db.execute(agent_query)
        agents = agent_result.all()
        
        if agents:
            # Find top performer
            top_agent = None
            best_rate = 0
            for agent in agents:
                if agent.total_assigned > 0:
                    rate = (agent.resolved_count or 0) / agent.total_assigned * 100
                    if rate > best_rate:
                        best_rate = rate
                        top_agent = agent
            
            if top_agent and best_rate >= 70:
                insights.append({
                    "type": "recommendation",
                    "priority": 3,
                    "title": f"Top Performer: {top_agent.name}",
                    "description": f"{round(best_rate)}% resolution rate on {top_agent.total_assigned} complaints. Consider routing complex cases to them.",
                    "action": "View Workload",
                    "actionUrl": "/users"
                })
        
        # 3. ANOMALY DETECTION: Check for unusual spikes
        # Calculate daily average over last 14 days
        two_weeks_ago = today - timedelta(days=14)
        avg_query = select(func.count()).select_from(Complaint).where(
            Complaint.org_id == org_id,
            Complaint.created_at >= two_weeks_ago,
            Complaint.created_at < today
        )
        result = await self.db.execute(avg_query)
        total_14_days = result.scalar() or 0
        daily_avg = total_14_days / 14 if total_14_days > 0 else 0
        
        # Count today and yesterday
        yesterday = today - timedelta(days=1)
        today_count = await self._count_since(org_id, today)
        
        yesterday_query = select(func.count()).select_from(Complaint).where(
            Complaint.org_id == org_id,
            Complaint.created_at >= yesterday,
            Complaint.created_at < today
        )
        result = await self.db.execute(yesterday_query)
        yesterday_count = result.scalar() or 0
        
        if daily_avg > 0:
            if yesterday_count > daily_avg * 1.5:
                spike_pct = round(((yesterday_count - daily_avg) / daily_avg) * 100)
                insights.append({
                    "type": "alert",
                    "priority": 1,
                    "title": f"Unusual Spike Yesterday (+{spike_pct}%)",
                    "description": f"Yesterday had {yesterday_count} complaints vs daily avg of {round(daily_avg)}. Investigate potential root cause.",
                    "action": "View Recent",
                    "actionUrl": "/complaints"
                })
            elif today_count > daily_avg * 1.5 and now.hour > 12:
                spike_pct = round(((today_count - daily_avg) / daily_avg) * 100)
                insights.append({
                    "type": "alert",
                    "priority": 1,
                    "title": f"Unusual Activity Today (+{spike_pct}%)",
                    "description": f"Already {today_count} complaints today vs daily avg of {round(daily_avg)}. Monitor closely.",
                    "action": "View Today",
                    "actionUrl": "/complaints"
                })
        
        # 4. WORKLOAD BALANCE: Check for overloaded agents
        workload = await self.get_workload_stats(org_id)
        overloaded = [w for w in workload if w.get('utilization', 0) > 80]
        underloaded = [w for w in workload if w.get('utilization', 0) < 30 and w.get('current_workload', 0) > 0]
        
        if overloaded and underloaded:
            insights.append({
                "type": "recommendation",
                "priority": 2,
                "title": "Workload Imbalance Detected",
                "description": f"{len(overloaded)} agent(s) overloaded (>80%), while {len(underloaded)} have light loads (<30%). Consider rebalancing.",
                "action": "Manage Team",
                    "actionUrl": "/users"
                })
        
        # Sort by priority (lower = more important)
        insights.sort(key=lambda x: x.get("priority", 5))
        
        return insights[:5]  # Return top 5 insights
