
import asyncio
import sys
import os
import logging

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.agents.email_parser_agent import EmailParserAgent
from app.services.email_service import email_service
from sqlalchemy import select
from app.models.organization import Organization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def trigger_parser():
    print("🚀 Triggering Email Parser Agent...")
    
    # Check config
    print(f"   Configured Email: {email_service.username}")
    print(f"   Configured Host:  {email_service.host}")
    
    async with AsyncSessionLocal() as db:
        # Get org
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        
        if not org:
            print("❌ No Organization found in DB.")
            return

        agent = EmailParserAgent(db, org.org_id)
        
        try:
            print("   Connecting to IMAP...")
            result = await agent.execute()
            
            # CRITICAL: Commit the transaction to persist changes
            await db.commit()
            
            print("✅ Execution Complete:")
            print(f"   Processed: {result.get('processed')}")
            print(f"   Created:   {result.get('created')}")
            print(f"   Message:   {result.get('message')}")
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trigger_parser())
