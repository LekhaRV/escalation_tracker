"""
Tarento AI Complaint Tracking System - System API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import os

from app.database import get_db
from app.config import settings

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    summary="Health check",
    description="Check system health: uptime, database, redis, version"
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """System health check"""
    # Check database
    db_status = "healthy"
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis
    redis_status = "healthy"
    try:
        from app.core.redis import redis_client
        await redis_client.set("health_check", "ok", expire=10)
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "components": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
        }
    }
