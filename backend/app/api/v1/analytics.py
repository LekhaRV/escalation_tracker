"""
Tarento AI Complaint Tracking System - Analytics API Endpoints
"""

from typing import Optional
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import AnalyticsResponse
from app.services.analytics_service import AnalyticsService
from app.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "",
    response_model=AnalyticsResponse,
    summary="Dashboard analytics",
    description="Get dashboard analytics including stats, patterns, and insights"
)
async def get_analytics(
    type: str = Query("dashboard", regex="^(dashboard|patterns|insights)$"),
    project_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get unified analytics based on type"""
    service = AnalyticsService(db)
    
    if type == "dashboard":
        data = await service.get_dashboard_stats(current_user.org_id)
    elif type == "patterns":
        data = {"patterns": await service.get_patterns(current_user.org_id)}
    elif type == "insights":
        data = {"insights": await service.get_insights(current_user.org_id)}
    else:
        data = await service.get_dashboard_stats(current_user.org_id)
    
    return AnalyticsResponse(
        type=type,
        generated_at=datetime.utcnow(),
        data=data
    )


@router.get(
    "/realtime",
    summary="Real-time metrics",
    description="Get current system status"
)
async def realtime_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time metrics"""
    service = AnalyticsService(db)
    stats = await service.get_dashboard_stats(current_user.org_id)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "active_complaints": stats["in_progress_complaints"],
        "critical": stats["critical_count"],
        "overdue": stats["overdue_complaints"],
        "sla_compliance": stats["sla_compliance_rate"]
    }


@router.get(
    "/workload",
    summary="Team workload",
    description="Get team member workload distribution"
)
async def get_workload(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get team workload statistics"""
    service = AnalyticsService(db)
    workload = await service.get_workload_stats(current_user.org_id)
    return {"workload": workload}


@router.get(
    "/escalations",
    summary="Projects in escalation",
    description="Get projects with critical/overdue complaints for dashboard"
)
async def get_escalations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get projects in escalation status"""
    service = AnalyticsService(db)
    escalations = await service.get_projects_in_escalation(current_user.org_id)
    return {"escalations": escalations}


@router.get(
    "/smart-insights",
    summary="AI-powered insights",
    description="Get intelligent insights including trend predictions, smart assignments, and anomaly detection"
)
async def get_smart_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated smart insights"""
    service = AnalyticsService(db)
    insights = await service.get_smart_insights(current_user.org_id)
    return {"insights": insights}

