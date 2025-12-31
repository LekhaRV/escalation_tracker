
import asyncio
import httpx
import sys
import os
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api/v1"

async def test_api():
    print("🌐 Testing API Response...")
    
    async with httpx.AsyncClient() as client:
        # 1. Login
        print("   - Logging in as admin...")
        try:
            # Login using form data
            login_res = await client.post(
                f"{BASE_URL}/auth/login",
                data={"username": "admin@tarento.com", "password": "admin123"},
            )
            login_res.raise_for_status()
            token = login_res.json()["access_token"]
            print("   ✅ Login successful")
        except Exception as e:
            print(f"   ❌ Login failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)
            return

        # 2. Get Analytics
        print("   - Fetching Analytics (type=dashboard)...")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            res = await client.get(f"{BASE_URL}/analytics?type=dashboard", headers=headers)
            res.raise_for_status()
            data = res.json()
            
            # 3. Inspect Payload
            print("\n🔍 API RESPONSE STRUCTURE:")
            # We expect data['data'] to contain our stats
            stats = data.get('data', {})
            
            # Check keys
            keys = list(stats.keys())
            print(f"   Top-level keys in 'data': {keys}")
            
            # Check daily_trends specifically
            trends = stats.get('daily_trends')
            if trends:
                print(f"   ✅ 'daily_trends' found with {len(trends)} items")
                print("   First item sample:")
                print(json.dumps(trends[0], indent=2))
            else:
                print("   ❌ 'daily_trends' MISSING or EMPTY in API response!")
                print(f"   Keys present: {stats.keys()}")

        except Exception as e:
            print(f"   ❌ API Call failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)

if __name__ == "__main__":
    asyncio.run(test_api())
