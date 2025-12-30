"""
Tarento AI Complaint Tracking System - Analytics Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, date

from app.utils.constants import PatternType, PatternStatus, InsightType, ImpactLevel


# Dashboard analytics
class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_complaints: int
    new_complaints: int
    in_progress_complaints: int
    resolved_complaints: int
    
    # SLA
    sla_compliance_rate: float
    overdue_complaints: int
    
    # By severity
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    
    # Trends
    complaints_today: int
    complaints_this_week: int
    complaints_this_month: int
    
    # Resolution
    avg_resolution_time_hours: float
    resolution_rate: float


class TrendDataPoint(BaseModel):
    """Single data point for trends"""
    date: str
    count: int
    category: Optional[str] = None


class TrendAnalytics(BaseModel):
    """Trend analytics data"""
    data_points: List[TrendDataPoint]
    period: str  # daily, weekly, monthly
    total: int
    change_percentage: float


# Pattern schemas
class PatternResponse(BaseModel):
    """Pattern response schema"""
    pattern_id: UUID
    pattern_type: PatternType
    pattern_description: Optional[str] = None
    affected_complaints: List[str] = []
    affected_projects: List[str] = []
    frequency: int
    severity_score: float
    status: PatternStatus
    detected_at: datetime
    
    class Config:
        from_attributes = True


# Insight schemas
class InsightResponse(BaseModel):
    """Insight response schema"""
    insight_id: UUID
    insight_type: InsightType
    title: str
    description: Optional[str] = None
    related_patterns: List[str] = []
    related_projects: List[str] = []
    impact_level: ImpactLevel
    actionable: bool
    generated_at: datetime
    
    class Config:
        from_attributes = True


# Analytics request
class AnalyticsRequest(BaseModel):
    """Analytics query parameters"""
    type: str = Field(
        default="dashboard",
        pattern="^(dashboard|trends|patterns|insights|executive|sla)$"
    )
    project_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    group_by: Optional[str] = Field(
        None,
        pattern="^(day|week|month|category|project|team)$"
    )


class ExportRequest(BaseModel):
    """Export request schema"""
    format: str = Field(default="csv", pattern="^(csv|excel|pdf)$")
    type: str = Field(
        default="complaints",
        pattern="^(complaints|analytics|reports)$"
    )
    filters: Optional[Dict[str, Any]] = None


# Analytics response
class AnalyticsResponse(BaseModel):
    """Unified analytics response"""
    type: str
    generated_at: datetime
    data: Dict[str, Any]


# SLA Report
class SLAReport(BaseModel):
    """SLA compliance report"""
    compliance_rate: float
    total_complaints: int
    within_sla: int
    breached: int
    
    by_severity: Dict[str, Dict[str, Any]]
    by_project: List[Dict[str, Any]]
    by_team: List[Dict[str, Any]]
    
    trending: str  # "improving", "stable", "declining"


# Executive Report
class ExecutiveReport(BaseModel):
    """Executive summary report"""
    period: str
    generated_at: datetime
    
    # High-level metrics
    total_complaints: int
    resolution_rate: float
    avg_resolution_time_hours: float
    sla_compliance: float
    
    # Top issues
    top_categories: List[Dict[str, Any]]
    top_projects: List[Dict[str, Any]]
    
    # Patterns and insights
    active_patterns: int
    new_insights: int
    
    # Recommendations
    recommendations: List[str]


# Agent status
class AgentStatusResponse(BaseModel):
    """Agent status response"""
    agent_name: str
    status: str  # "running", "idle", "error"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time_ms: float
    
    # Recent logs
    recent_logs: List[Dict[str, Any]] = []


class AllAgentsResponse(BaseModel):
    """All agents status"""
    agents: List[AgentStatusResponse]
    scheduler_status: str


# Realtime metrics
class RealtimeMetrics(BaseModel):
    """Real-time metrics for SSE"""
    timestamp: datetime
    new_complaints_last_hour: int
    active_complaints: int
    sla_warnings: int  # Approaching SLA deadline
    sla_breaches: int  # Already breached
    
    # By status
    by_status: Dict[str, int]
