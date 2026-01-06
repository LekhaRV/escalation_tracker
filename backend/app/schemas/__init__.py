"""
Tarento AI Complaint Tracking System - Schemas Module
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRegister,
    UserLogin,
    UserUpdate,
    UserAdminUpdate,
    UserResponse,
    UserBriefResponse,
    TokenResponse,
    TokenRefresh,
    UserListResponse
)

from app.schemas.complaint import (
    ComplaintCategoryResponse,
    ComplaintAssignmentResponse,
    ComplaintEscalationResponse,
    ComplaintBase,
    ComplaintCreate,
    ComplaintUpdate,
    ComplaintBulkRequest,
    ComplaintBriefResponse,
    ComplaintDetailResponse,
    ComplaintListResponse,
    ComplaintListResponse,
    ComplaintBulkResponse,
    AssignableUserResponse,
    ComplaintCommentResponse,
    ComplaintCommentCreate
)

from app.schemas.project import (
    TeamMemberResponse,
    TeamMemberManage,
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectBriefResponse,
    ProjectDetailResponse,
    ProjectListResponse
)

from app.schemas.analytics import (
    DashboardStats,
    TrendDataPoint,
    TrendAnalytics,
    PatternResponse,
    InsightResponse,
    AnalyticsRequest,
    ExportRequest,
    AnalyticsResponse,
    SLAReport,
    ExecutiveReport,
    AgentStatusResponse,
    AllAgentsResponse,
    RealtimeMetrics
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "UserAdminUpdate",
    "UserResponse",
    "UserBriefResponse",
    "TokenResponse",
    "TokenRefresh",
    "UserListResponse",
    # Complaint
    "ComplaintCategoryResponse",
    "ComplaintAssignmentResponse",
    "ComplaintEscalationResponse",
    "ComplaintBase",
    "ComplaintCreate",
    "ComplaintUpdate",
    "ComplaintBulkRequest",
    "ComplaintBriefResponse",
    "ComplaintDetailResponse",
    "ComplaintListResponse",
    "ComplaintListResponse",
    "ComplaintListResponse",
    "ComplaintListResponse",
    "ComplaintBulkResponse",
    "AssignableUserResponse",
    "ComplaintCommentResponse",
    "ComplaintCommentCreate",
    # Project
    "TeamMemberResponse",
    "TeamMemberManage",
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectBriefResponse",
    "ProjectDetailResponse",
    "ProjectListResponse",
    # Analytics
    "DashboardStats",
    "TrendDataPoint",
    "TrendAnalytics",
    "PatternResponse",
    "InsightResponse",
    "AnalyticsRequest",
    "ExportRequest",
    "AnalyticsResponse",
    "SLAReport",
    "ExecutiveReport",
    "AgentStatusResponse",
    "AllAgentsResponse",
    "RealtimeMetrics"
]
