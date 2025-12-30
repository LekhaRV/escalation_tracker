"""
Tarento AI Complaint Tracking System
Main FastAPI Application with Comprehensive OpenAPI Documentation
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.database import init_db, close_db
from app.api.v1 import api_router
from app.core.logging import logger
from app.core.exceptions import AppError


# OpenAPI documentation
OPENAPI_DESCRIPTION = """
# Tarento AI Complaint Tracking System API

AI-powered complaint management system for Tarento Technologies with intelligent routing and organization-wide visibility.

## Overview

This API provides complete complaint lifecycle management:
- **Email Ingestion**: Auto-ingest complaints from email (IMAP) every 5 minutes
- **AI Categorization**: Google Gemini categorizes by type, severity, department within 2 minutes
- **Project-Based Routing**: Complaints linked to projects route to team members using score-based assignment
- **SLA Monitoring**: Auto-escalation based on severity (Critical: 4h, High: 24h, Medium: 72h, Low: 168h)
- **Pattern Detection**: Daily analysis identifies recurring issues
- **Executive Insights**: Weekly AI-generated insights and recommendations

## Authentication

All endpoints (except /health) require JWT Bearer token authentication.

```
Authorization: Bearer <access_token>
```

### Token Lifecycle
- **Access Token**: 30 minutes validity
- **Refresh Token**: 7 days validity
- Use `/auth/refresh` to get new tokens before expiry

## Rate Limiting

- **General endpoints**: 60 requests/minute
- **Auth endpoints**: 5 requests/15 minutes

## Organization-Wide Visibility

**KEY PRINCIPLE**: ALL roles see ALL data in their organization. Roles control ACTIONS, not VISIBILITY.

| Role | View All Data | Manage Users | Manage Projects | Manage Complaints | Delete |
|------|---------------|--------------|-----------------|-------------------|--------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manager | ✅ | Limited | ✅ | ✅ | ❌ |
| Agent | ✅ | ❌ | ❌ | Self-assign only | ❌ |
| Viewer | ✅ | ❌ | ❌ | ❌ | ❌ |

## Categories

Tarento-specific complaint categories:
- `project_delivery`: Milestone delays, scope creep, quality issues
- `technical`: Architecture, performance, integration, security
- `communication`: Delayed updates, unclear requirements
- `resource`: Team unavailability, skill mismatch
- `billing`: Invoice discrepancies, rate disagreements
- `quality`: Code review failures, non-compliance
- `support`: Slow bug resolution, SLA breaches
- `engagement`: Expectation mismatch, stakeholder issues

## Project-Based Routing

When a complaint is linked to a project:
1. Get project team members
2. Score each member: Role (0-40) + Specialization (0-40) + Workload (0-20)
3. Apply severity multiplier (Critical: 1.3x, High: 1.2x)
4. Assign to highest scoring member with capacity

If no project linked, fallback to category→department mapping.

## Error Responses

All errors return JSON with `detail` field:

```json
{
    "detail": "Error message here"
}
```

| Status | Description |
|--------|-------------|
| 400 | Validation error |
| 401 | Invalid/expired token |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (duplicate) |
| 422 | Unprocessable entity |
| 500 | Internal server error |
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Tarento Complaint Tracking System...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")
    await close_db()


app = FastAPI(
    title="Tarento AI Complaint Tracking System",
    description=OPENAPI_DESCRIPTION,
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Tarento Support",
        "email": "support@tarento.com"
    },
    license_info={
        "name": "Proprietary",
    },
    openapi_tags=[
        {"name": "Authentication", "description": "User registration, login, and token management"},
        {"name": "Complaints", "description": "Complaint CRUD with org-wide visibility"},
        {"name": "Projects", "description": "Project and team management"},
        {"name": "Analytics", "description": "Dashboard, reports, patterns, and insights"},
        {"name": "Admin", "description": "User and organization management"},
        {"name": "Agents", "description": "AI agent status and manual triggers"},
        {"name": "System", "description": "Health checks and system info"}
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "errors": exc.details}
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "Tarento AI Complaint Tracking System",
        "version": "1.0.0",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
