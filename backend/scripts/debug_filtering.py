
import asyncio
import sys
import os
import logging

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gemini_service import gemini_service
# import app.services.gemini_service as gs_module
# print(f"DEBUG: Loaded gemini_service from: {gs_module.__file__}")

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_filtering():
    print("\n🔬  Testing Gemini Filtering Logic...\n")
    
    scenarios = [
        {
            "name": "Holiday Inquiry",
            "subject": "Holiday Calendar Question",
            "content": "Hi team, just wanted to check if we have next Friday off for the local holiday? Thanks, John."
        },
        {
            "name": "API Failure",
            "subject": "Critical API Failure",
            "content": "The API is down returning 500s."
        }
    ]

    for s in scenarios:
        print(f"\n--- Testing: {s['name']} ---")
        try:
            print("Sending to Gemini...")
            result = await gemini_service.categorize_complaint(s['subject'], s['content'])
            print(f"Result: {result}")
            print(f"Is Complaint? {result.get('is_complaint')}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_filtering())
