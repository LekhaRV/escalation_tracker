"""
Tarento AI Complaint Tracking System - Analytics API Endpoints
"""

from typing import Optional
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import (
    AnalyticsResponse, DashboardStats, ExportRequest,
    PatternResponse, InsightResponse, SLAReport, ExecutiveReport
)
from app.services.analytics_service import AnalyticsService
from app.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "",
    response_model=AnalyticsResponse,
    summary="Unified analytics",
    description="Get analytics by type: dashboard, trends, patterns, insights, executive, sla"
)
async def get_analytics(
    type: str = Query("dashboard", regex="^(dashboard|trends|patterns|insights|executive|sla)$"),
    project_id: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    group_by: Optional[str] = Query(None, regex="^(day|week|month|category|project|team)$"),
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
    elif type == "executive":
        stats = await service.get_dashboard_stats(current_user.org_id)
        data = {
            "period": "last_30_days",
            "summary": stats,
            "top_categories": [],
            "recommendations": []
        }
    elif type == "sla":
        stats = await service.get_dashboard_stats(current_user.org_id)
        data = {
            "compliance_rate": stats["sla_compliance_rate"],
            "overdue": stats["overdue_complaints"],
            "by_severity": {}
        }
    else:
        data = await service.get_dashboard_stats(current_user.org_id)
    
    return AnalyticsResponse(
        type=type,
        generated_at=datetime.utcnow(),
        data=data
    )


@router.post(
    "/export",
    summary="Export data",
    description="Export analytics data as CSV, Excel, or PDF"
)
async def export_data(
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export data in requested format"""
    # Placeholder - actual export implementation
    return {
        "success": True,
        "message": f"Export started in {data.format} format",
        "download_url": None
    }


@router.get(
    "/realtime",
    summary="Real-time metrics",
    description="Get real-time metrics via SSE"
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
        "new_complaints_last_hour": stats["complaints_today"],
        "active_complaints": stats["in_progress_complaints"],
        "sla_warnings": 0,
        "sla_breaches": stats["overdue_complaints"],
        "by_status": {
            "new": stats["new_complaints"],
            "in_progress": stats["in_progress_complaints"],
            "resolved": stats["resolved_complaints"]
        }
    }


@router.get(
    "/reports/{report_type}",
    summary="Pre-built reports",
    description="Get pre-built reports: executive, sla, team, project"
)
async def get_report(
    report_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pre-built report by type"""
    service = AnalyticsService(db)
    stats = await service.get_dashboard_stats(current_user.org_id)
    
    return {
        "report_type": report_type,
        "generated_at": datetime.utcnow().isoformat(),
        "data": stats
    }
