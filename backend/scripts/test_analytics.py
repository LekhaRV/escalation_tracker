
import asyncio
import sys
import os
from pprint import pprint

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.analytics_service import AnalyticsService
from app.agents.analyst_agent import AnalystAgent
from app.models.organization import Organization
from sqlalchemy import select

async def test_analytics():
    print("Testing Analytics Service...")
    async with AsyncSessionLocal() as db:
        # Get default org
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        
        if not org:
            print("No organization found!")
            return
            
        service = AnalyticsService(db)
        stats = await service.get_dashboard_stats(org.org_id)
        print("\n--- Dashboard Stats ---")
        print("--- DAILY TRENDS JSON START ---")
        import json
        print(json.dumps(stats.get('daily_trends', []), indent=2))
        print("--- DAILY TRENDS JSON END ---")
        return # STOP HERE to prevent noise
            
        print("\n--- Testing Analyst Agent ---")
        agent = AnalystAgent(db, org.org_id)
        query = "How many critical complaints do we have?"
        response = await agent.answer_query(query)
        print(f"Query: {query}")
        print(f"Intent: {response['intent']}")
        print(f"Answer: {response['answer']}")

if __name__ == "__main__":
    asyncio.run(test_analytics())
