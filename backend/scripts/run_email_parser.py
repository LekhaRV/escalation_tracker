
import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.organization import Organization
from app.agents.email_parser_agent import EmailParserAgent
from sqlalchemy import select

async def force_run():
    print("Force running Email Parser Agent...")
    async with AsyncSessionLocal() as db:
        # Get default org
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        
        if not org:
            print("No organization found!")
            return
            
        agent = EmailParserAgent(db, org.org_id)
        result = await agent.execute()
        await db.commit()
        print(f"Agent Finished: {result}")

if __name__ == "__main__":
    asyncio.run(force_run())
