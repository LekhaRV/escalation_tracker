"""
Tarento AI Complaint Tracking System - Services Module
"""

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.complaint_service import ComplaintService
from app.services.project_service import ProjectService
from app.services.gemini_service import gemini_service
from app.services.email_service import email_service
from app.services.notification_service import notification_service
from app.services.analytics_service import AnalyticsService

__all__ = [
    "AuthService",
    "UserService",
    "ComplaintService",
    "ProjectService",
    "gemini_service",
    "email_service",
    "notification_service",
    "AnalyticsService"
]
