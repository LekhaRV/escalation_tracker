
import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.agents.pattern_agent import PatternAgent
from sqlalchemy import select
from app.models.organization import Organization

async def run_patterns():
    print("🧩 Running Pattern Agent...")
    async with AsyncSessionLocal() as db:
        # Get org
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        if not org:
            print("No org found")
            return

        agent = PatternAgent(db, org.org_id)
        result = await agent.execute()
        
        print(f"✅ Pattern Agent Result: {result}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_patterns())
