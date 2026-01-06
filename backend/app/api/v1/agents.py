"""
Tarento AI Complaint Tracking System - Agents API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.database import get_db
from app.models import User, AgentLog
from app.schemas import AllAgentsResponse, AgentStatusResponse
from app.api.deps import get_current_user, require_admin_or_manager
from app.utils.constants import AgentLogStatus
from app.core.scheduler import (
    run_email_parser_job,
    run_categorization_agent_job,
    run_mapping_agent_job,
    run_escalation_agent_job,
    run_pattern_agent_job,
    run_insight_agent_job
)

router = APIRouter(prefix="/agents", tags=["Agents"])

AGENT_NAMES = [
    "email_parser",
    "categorization",
    "mapping",
    "escalation",
    "pattern",
    "insight"
]


@router.get(
    "",
    response_model=AllAgentsResponse,
    summary="Get all agents status",
    description="Get status, stats, and recent logs for all AI agents"
)
async def get_agents_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get status of all agents"""
    agents = []
    
    for name in AGENT_NAMES:
        # Get stats for this agent
        total = await db.execute(
            select(func.count()).where(AgentLog.agent_name == name)
        )
        success = await db.execute(
            select(func.count()).where(
                AgentLog.agent_name == name,
                AgentLog.status == AgentLogStatus.SUCCESS
            )
        )
        failed = await db.execute(
            select(func.count()).where(
                AgentLog.agent_name == name,
                AgentLog.status == AgentLogStatus.FAILURE
            )
        )
        
        # Get last run
        last_run_result = await db.execute(
            select(AgentLog.executed_at).where(
                AgentLog.agent_name == name
            ).order_by(AgentLog.executed_at.desc()).limit(1)
        )
        last_run = last_run_result.scalar_one_or_none()
        
        # Get recent logs
        recent_result = await db.execute(
            select(AgentLog).where(
                AgentLog.agent_name == name
            ).order_by(AgentLog.executed_at.desc()).limit(5)
        )
        recent_logs = [
            {
                "log_id": str(log.log_id),
                "status": log.status.value,
                "executed_at": log.executed_at.isoformat() if log.executed_at else None,
                "execution_time_ms": log.execution_time_ms
            }
            for log in recent_result.scalars().all()
        ]
        
        agents.append(AgentStatusResponse(
            agent_name=name,
            status="idle",
            last_run=last_run,
            next_run=None,
            total_executions=total.scalar() or 0,
            successful_executions=success.scalar() or 0,
            failed_executions=failed.scalar() or 0,
            avg_execution_time_ms=0.0,
            recent_logs=recent_logs
        ))
    
    return AllAgentsResponse(
        agents=agents,
        scheduler_status="running"
    )


@router.post(
    "/{agent_name}/run",
    summary="Trigger agent manually",
    description="Manually trigger an AI agent to run immediately"
)
async def run_agent(
    agent_name: str,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Manually trigger an agent"""
    if agent_name not in AGENT_NAMES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agent: {agent_name}. Valid agents: {AGENT_NAMES}"
        )
    
    # Create log entry for manual trigger
    log = AgentLog(
        agent_name=agent_name,
        input_data={"triggered_by": current_user.email, "manual": True},
        output_data={},
        status=AgentLogStatus.SUCCESS,
        execution_time_ms=0
    )
    db.add(log)
    await db.commit()
    
    # Map agent name to job function
    jobs = {
        "email_parser": run_email_parser_job,
        "categorization": run_categorization_agent_job,
        "mapping": run_mapping_agent_job,
        "escalation": run_escalation_agent_job,
        "pattern": run_pattern_agent_job,
        "insight": run_insight_agent_job
    }
    
    if agent_name in jobs:
        background_tasks.add_task(jobs[agent_name])
    
    return {
        "success": True,
        "agent_name": agent_name,
        "message": f"Agent {agent_name} triggered successfully",
        "log_id": str(log.log_id)
    }
