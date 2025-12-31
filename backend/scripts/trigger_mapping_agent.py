
import asyncio
import sys
import os
import logging

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.agents.mapping_agent import MappingAgent
from sqlalchemy import select
from app.models.organization import Organization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def trigger_mapping():
    print("🚀 Triggering Mapping Agent...")
    
    async with AsyncSessionLocal() as db:
        # Get org
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        
        if not org:
            print("❌ No Organization found in DB.")
            return

        agent = MappingAgent(db, org.org_id)
        
        try:
            print("   Running routing logic...")
            result = await agent.execute()
            print("✅ Execution Complete:")
            print(f"   Processed: {result.get('processed')}")
            print(f"   Assigned:  {result.get('assigned')}")
            print(f"   Message:   {result.get('message')}")
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trigger_mapping())
