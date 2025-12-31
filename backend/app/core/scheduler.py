"""
Tarento AI Complaint Tracking System - Scheduler
Manages background agent execution using APScheduler
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.organization import Organization
from app.agents.email_parser_agent import EmailParserAgent
from app.agents.categorization_agent import CategorizationAgent
from app.agents.mapping_agent import MappingAgent

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def heartbeat():
    print("💓 Scheduler Heartbeat: Alive")

async def get_default_org_id(db):
    """Get the first active organization for single-tenant agent execution"""
    result = await db.execute(select(Organization).limit(1))
    org = result.scalars().first()
    return org.org_id if org else None

async def run_email_parser_job():
    """Job to run Email Parser Agent"""
    async with AsyncSessionLocal() as db:
        org_id = await get_default_org_id(db)
        if not org_id:
            logger.warning("Agent Job Skipped: No organization found")
            return
            
        agent = EmailParserAgent(db, org_id)
        await agent.run()
        await db.commit()

async def run_mapping_agent_job():
    """Job to run Mapping Agent (Auto-Assign)"""
    async with AsyncSessionLocal() as db:
        org_id = await get_default_org_id(db)
        if not org_id:
            return
            
        agent = MappingAgent(db, org_id)
        await agent.run()
        await db.commit()

def start_scheduler():
    """Start the APScheduler"""
    # Email Parser (Default: Every 2 minutes for demo purposes, or config)
    # Using specific CronTrigger to parse the setting string if needed, 
    # but for now simplicity: fixed interval for verified agents
    
    # settings.AGENT_EMAIL_PARSER_SCHEDULE is like "*/5 * * * *"
    # Simpler to just use interval for dev
    
    # 1. Email Parser
    scheduler.add_job(
        run_email_parser_job,
        'interval',
        minutes=5,
        id='email_parser_agent',
        replace_existing=True
    )
    logger.info("Added job: Email Parser Agent (every 5 mins)")
    
    # 2. Mapping Agent (runs more often to catch new complaints)
    scheduler.add_job(
        run_mapping_agent_job,
        'interval',
        minutes=3,
        id='mapping_agent',
        replace_existing=True
    )
    logger.info("Added job: Mapping Agent (every 3 mins)")

    # scheduler.start() removed
    logger.info("Added job: Mapping Agent (every 3 mins)")

    # 3. Heartbeat
    scheduler.add_job(heartbeat, 'interval', seconds=10, id='heartbeat', replace_existing=True)
    
    # Check if running before starting
    if not scheduler.running:
        scheduler.start()
    print("✅✅✅ AGENT SCHEDULER STARTED ✅✅✅", flush=True)
    logger.info("Agent Scheduler started")

def shutdown_scheduler():
    """Shutdown the scheduler"""
    scheduler.shutdown()
    logger.info("Agent Scheduler shut down")
