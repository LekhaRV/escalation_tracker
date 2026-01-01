
import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.database import async_session_factory
from app.services.project_service import ProjectService
from app.models import User
from sqlalchemy import select

async def verify():
    print("Connecting to DB...")
    async with async_session_factory() as db:
        # Get Admin User to use as context
        result = await db.execute(select(User))
        users = result.scalars().all()
        if not users:
            print("No users found.")
            return
        admin_user = users[0]
        print(f"Using Context User: {admin_user.email}")

        print("\nTesting ProjectService.get_projects...")
        service = ProjectService(db)
        try:
            # Replicate the call from projects.py list_projects
            results = await service.get_projects(
                org_id=admin_user.org_id,
                page=1,
                page_size=20
            )
            print(f"Service returned {len(results['items'])} projects.")
            for p in results['items']:
                print(f"Project: {p.project_name}, Complaints: {getattr(p, 'complaints_count', 'N/A')}")
                
        except Exception as e:
            print(f"ProjectService Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify())
