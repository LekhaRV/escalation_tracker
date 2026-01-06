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
from app.agents.escalation_agent import EscalationAgent
from app.agents.pattern_agent import PatternAgent
from app.agents.insight_agent import InsightAgent

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

async def run_categorization_agent_job():
    """Job to run Categorization Agent - categorize uncategorized complaints"""
    async with AsyncSessionLocal() as db:
        org_id = await get_default_org_id(db)
        if not org_id:
            return
            
        agent = CategorizationAgent(db, org_id)
        result = await agent.run()
        await db.commit()
        logger.info(f"CategorizationAgent: {result.output_data.get('message', 'done')}")

async def run_mapping_agent_job():
    """Job to run Mapping Agent (Auto-Assign)"""
    async with AsyncSessionLocal() as db:
        org_id = await get_default_org_id(db)
        if not org_id:
            return
            
        agent = MappingAgent(db, org_id)
        await agent.run()
        await db.commit()

async def run_escalation_agent_job():
    """Job to run Escalation Agent - SLA monitoring and warnings"""
    async with AsyncSessionLocal() as db:
        org_id = await get_default_org_id(db)
        if not org_id:
            return
            
        agent = EscalationAgent(db, org_id)
        result = await agent.run()
        await db.commit()
        logger.info(f"EscalationAgent: {result.output_data.get('message', 'done')}")

async def run_pattern_agent_job():
    """Job to run Pattern Agent - detect recurring patterns"""
    async with AsyncSessionLocal() as db:
        org_id = await get_default_org_id(db)
        if not org_id:
            return
            
        agent = PatternAgent(db, org_id)
        result = await agent.run()
        await db.commit()
        logger.info(f"PatternAgent: {result.output_data.get('message', 'done')}")

async def run_insight_agent_job():
    """Job to run Insight Agent - generate executive insights"""
    async with AsyncSessionLocal() as db:
        org_id = await get_default_org_id(db)
        if not org_id:
            return
            
        agent = InsightAgent(db, org_id)
        result = await agent.run()
        await db.commit()
        logger.info(f"InsightAgent: {result.output_data.get('message', 'done')}")

def start_scheduler():
    """Start the APScheduler with all AI agents"""
    
    # 1. Email Parser Agent - Every 5 minutes
    scheduler.add_job(
        run_email_parser_job,
        'interval',
        minutes=5,
        id='email_parser_agent',
        replace_existing=True
    )
    logger.info("Added job: Email Parser Agent (every 5 mins)")
    
    # 2. Categorization Agent - Every 2 minutes
    scheduler.add_job(
        run_categorization_agent_job,
        'interval',
        minutes=2,
        id='categorization_agent',
        replace_existing=True
    )
    logger.info("Added job: Categorization Agent (every 2 mins)")
    
    # 3. Mapping Agent - Every 3 minutes
    scheduler.add_job(
        run_mapping_agent_job,
        'interval',
        minutes=3,
        id='mapping_agent',
        replace_existing=True
    )
    logger.info("Added job: Mapping Agent (every 3 mins)")
    
    # 4. Escalation Agent - Every 1 hour
    scheduler.add_job(
        run_escalation_agent_job,
        'interval',
        hours=1,
        id='escalation_agent',
        replace_existing=True
    )
    logger.info("Added job: Escalation Agent (every 1 hour)")
    
    # 5. Pattern Agent - Every 6 hours
    scheduler.add_job(
        run_pattern_agent_job,
        'interval',
        hours=6,
        id='pattern_agent',
        replace_existing=True
    )
    logger.info("Added job: Pattern Agent (every 6 hours)")
    
    # 6. Insight Agent - Every 12 hours
    scheduler.add_job(
        run_insight_agent_job,
        'interval',
        hours=12,
        id='insight_agent',
        replace_existing=True
    )
    logger.info("Added job: Insight Agent (every 12 hours)")

    # Heartbeat - Every 10 seconds
    scheduler.add_job(heartbeat, 'interval', seconds=10, id='heartbeat', replace_existing=True)
    
    # Start scheduler if not running
    if not scheduler.running:
        scheduler.start()
    print("✅✅✅ AGENT SCHEDULER STARTED - ALL 6 AGENTS ENABLED ✅✅✅", flush=True)
    logger.info("Agent Scheduler started with all 6 agents")

def shutdown_scheduler():
    """Shutdown the scheduler"""
    scheduler.shutdown()
    logger.info("Agent Scheduler shut down")

