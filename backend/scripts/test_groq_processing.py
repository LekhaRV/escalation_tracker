
import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.email_service import email_service
from app.config import settings

async def test_groq():
    print(f"Testing Groq Integration with Key: {settings.GROQ_API_KEY[:5]}...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Simulate an email
            await email_service.process_simulated_email(
                subject="Groq Test: High Latency in Billing API",
                content="The billing service api is responding very slowly. Customers are complaining about timeouts. Please investigate immediately.",
                sender="test_groq@tarento.com",
                db_session=db
            )
            await db.commit()
            print("✅ processing complete.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq())
