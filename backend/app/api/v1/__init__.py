"""
Tarento AI Complaint Tracking System - API v1 Router
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.complaints import router as complaints_router
from app.api.v1.projects import router as projects_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.admin import router as admin_router
from app.api.v1.agents import router as agents_router
from app.api.v1.system import router as system_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(complaints_router)
api_router.include_router(projects_router)
api_router.include_router(analytics_router)
api_router.include_router(admin_router)
api_router.include_router(agents_router)
api_router.include_router(system_router)
