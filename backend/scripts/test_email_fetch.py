
import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_service import email_service
from app.core.logging import logger

# Set logger to print to console
import logging
logging.basicConfig(level=logging.INFO)

async def test_fetch():
    print("Testing Email Fetch...")
    try:
        emails = await email_service.fetch_new_emails()
        print(f"Success! Fetched {len(emails)} emails.")
        for e in emails:
            print(f"- Subject: {e.get('subject')}")
            print(f"- Sender: {e.get('sender')}")
            print(f"- Content Preview: {e.get('content')[:50]}...")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error fetching emails: {e}")

if __name__ == "__main__":
    asyncio.run(test_fetch())
