
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.database import async_session_factory
from app.services.user_service import UserService
from app.models import User
from sqlalchemy import select

async def verify():
    print("Connecting to DB...")
    async with async_session_factory() as db:
        # 1. Check Total Users
        result = await db.execute(select(User))
        users = result.scalars().all()
        print(f"Total Users in DB: {len(users)}")
        
        if not users:
            print("No users found! DB is empty.")
            return

        admin_user = users[0]
        print(f"First User: {admin_user.email}, Role: {admin_user.role}, Org: {admin_user.org_id}")

        # 2. Test Service Query
        print("\nTesting UserService.get_users_with_stats...")
        service = UserService(db)
        try:
            stats = await service.get_users_with_stats(org_id=admin_user.org_id)
            print(f"Service returned {len(stats['items'])} items.")
            
            if stats['items']:
                u = stats['items'][0]
                print(f"Sample User Stats: Escalations={getattr(u, 'escalations_count', 'N/A')}, Resolutions={getattr(u, 'resolutions_count', 'N/A')}")
                
        except Exception as e:
            print(f"Service Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify())
