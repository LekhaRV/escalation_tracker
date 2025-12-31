
import asyncio
import sys
import os
import logging

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.email_service import email_service

# Configure logging to show only our output
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("agent_test")
logger.setLevel(logging.INFO)

async def test_scenarios():
    print("\n🤖  Testing AI Agent Behavior...\n")
    print("="*60)
    
    scenarios = [
        {
            "type": "✅ Valid Complaint",
            "subject": "Critical API Failure in Production",
            "content": "The Payments API is returning 500 errors for all transactions since 10 AM. This is blocking all checkouts for the Phoenix Project. Please fix urgently.",
            "sender": "client@enterprise.com"
        },
        {
            "type": "❌ Non-Complaint (Inquiry)",
            "subject": "Holiday Calendar Question",
            "content": "Hi team, just wanted to check if we have next Friday off for the local holiday? Thanks, John.",
            "sender": "john@tarento.com"
        }
    ]

    async with AsyncSessionLocal() as db:
        for scenario in scenarios:
            print(f"\n📨  Simulating: {scenario['type']}")
            print(f"    Subject: {scenario['subject']}")
            print(f"    Body:    {scenario['content'][:80]}...")
            
            print("    Thinking... 🧠")
            
            try:
                result = await email_service.process_simulated_email(
                    subject=scenario["subject"],
                    content=scenario["content"],
                    sender=scenario["sender"],
                    db_session=db
                )
                
                print(f"    👉 AI Decision:")
                print(f"       Category:  {result.get('category').upper()}")
                print(f"       Severity:  {result.get('severity').upper()}")
                print(f"       Action:    {'Assigned to Engineer' if result.get('assigned') else 'Unassigned (Backlog)'}")
                print(f"       ID:        {result.get('complaint_id')}")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_scenarios())
