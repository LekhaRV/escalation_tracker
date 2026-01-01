
import asyncio
import os
import sys
from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add parent dir to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.config import settings
from app.models import ComplaintAssignment

async def fix_deadlines():
    """Update all existing SLA deadlines to assigned_at + 60 days"""
    print("🔌 Connecting to database...")
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔍 Fetching assignments...")
        result = await session.execute(select(ComplaintAssignment))
        assignments = result.scalars().all()
        
        print(f"📝 Found {len(assignments)} assignments. Updating deadlines...")
        
        count = 0
        for assignment in assignments:
            if assignment.assigned_at:
                # Set to 60 days from assignment time
                new_deadline = assignment.assigned_at + timedelta(days=60)
                assignment.sla_deadline = new_deadline
                count += 1
        
        await session.commit()
        print(f"✅ Successfully updated {count} assignments to 60-day SLA.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_deadlines())
