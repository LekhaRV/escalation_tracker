import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.project_service import ProjectService
from app.models import User, Project
from app.schemas import TeamMemberManage
from app.core.exceptions import AuthorizationError
from sqlalchemy import select

async def verify_affinity():
    async with AsyncSessionLocal() as db:
        print("Starting Team Affinity Verification...")
        
        # 1. Fetch Admin (to perform the action)
        result = await db.execute(select(User).where(User.role == "ADMIN").limit(1))
        admin = result.scalar_one()
        
        # 2. Fetch Project (Delivery Dept)
        result = await db.execute(select(Project).where(Project.project_name == "E-Gov Platform"))
        p_delivery = result.scalar_one()
        
        # 3. Fetch User (Engineering Dept - Dev1)
        result = await db.execute(select(User).where(User.email == "dev1@tarento.com"))
        user_engineering = result.scalar_one()
        
        print(f"Project Dept: {p_delivery.department_id}")
        print(f"User Dept: {user_engineering.department_id}")
        
        project_service = ProjectService(db)

        print("\n[TEST] Adding Engineering User to Delivery Project...")
        try:
            await project_service.manage_team(
                p_delivery.project_id, 
                p_delivery.org_id, 
                TeamMemberManage(
                    user_id=user_engineering.user_id,
                    action="add",
                    role="Guest Dev"
                ),
                admin
            )
            print("❌ Success (Unexpected - Should Fail)")
        except AuthorizationError as e:
            print(f"✅ Blocked: {e}")
        except Exception as e:
            print(f"❌ Failed with unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_affinity())
