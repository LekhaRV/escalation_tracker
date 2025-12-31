
import asyncio
import httpx
import os
import sys

# Add parent dir to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

async def list_models(version):
    api_key = settings.GEMINI_API_KEY
    url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
    print(f"\n--- Listing Models on {version} ---")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                models = response.json().get('models', [])
                names = [m['name'] for m in models]
                print(f"✅ Available Models ({len(names)}):")
                for n in names:
                    print(f" - {n}")
                return names
            else:
                print(f"❌ FAILED: {response.text[:200]}")
                return []
    except Exception as e:
        print(f"Exception: {str(e)}")
        return []

async def main():
    if not settings.GEMINI_API_KEY:
        print("❌ ERROR: No API Key")
        return

    # 1. List Models to verify access
    await list_models("v1beta")

    # 2. Test specific endpoints if needed (commented out for speed)
    # matrix = ...
    # for model, version in matrix: ... 

if __name__ == "__main__":
    asyncio.run(main())
