import asyncio
import sys
import os
from uuid import uuid4

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.project_service import ProjectService
from app.services.complaint_service import ComplaintService
from app.models import User, Project, Complaint, ComplaintAssignment
from app.schemas import ProjectUpdate, ComplaintUpdate
from app.core.exceptions import AuthorizationError
from sqlalchemy import select
from app.utils.constants import ComplaintStatus

async def verify_permissions():
    async with AsyncSessionLocal() as db:
        print("Starting Permission Verification...")
        
        # 1. Fetch Actors
        # Manager (Delivery)
        result = await db.execute(select(User).where(User.email == "manager@tarento.com"))
        manager = result.scalar_one()
        
        # Dev1 (Engineering)
        result = await db.execute(select(User).where(User.email == "dev1@tarento.com"))
        dev1 = result.scalar_one()

        # Dev2 (Engineering)
        result = await db.execute(select(User).where(User.email == "dev2@tarento.com"))
        dev2 = result.scalar_one()
        
        # 2. Fetch Resources
        # Project in Delivery (Manager's Dept)
        result = await db.execute(select(Project).where(Project.project_name == "E-Gov Platform"))
        p1_delivery = result.scalar_one()
        
        # Project in Engineering (Not Manager's Dept)
        result = await db.execute(select(Project).where(Project.project_name == "FinTech App"))
        p2_engineering = result.scalar_one()
        
        project_service = ProjectService(db)
        complaint_service = ComplaintService(db)

        # ==========================================
        # TEST GROUP 1: Manager Permissions
        # ==========================================
        print("\n[TEST 1] Manager updating OWN Dept Project...")
        try:
            await project_service.update_project(
                p1_delivery.project_id, 
                p1_delivery.org_id, 
                ProjectUpdate(description="Updated by Manager"), 
                manager
            )
            print("✅ Success (Expected)")
        except Exception as e:
            print(f"❌ Failed: {e}")

        print("\n[TEST 2] Manager updating OTHER Dept Project...")
        try:
            await project_service.update_project(
                p2_engineering.project_id, 
                p2_engineering.org_id, 
                ProjectUpdate(description="Hacked by Manager"), 
                manager
            )
            print("❌ Success (Unexpected - Should Fail)")
        except AuthorizationError:
            print("✅ Blocked (Expected)")
        except Exception as e:
            print(f"❌ Failed with unexpected error: {e}")

        # ==========================================
        # TEST GROUP 2: Agent Permissions
        # ==========================================
        
        # Find a complaint assigned to Dev1
        result = await db.execute(select(Complaint).join(ComplaintAssignment).where(ComplaintAssignment.assigned_to_user_id == dev1.user_id).limit(1))
        c_assigned_to_dev1 = result.scalar_one_or_none()
        
        # Find a complaint assigned to Dev2
        result = await db.execute(select(Complaint).join(ComplaintAssignment).where(ComplaintAssignment.assigned_to_user_id == dev2.user_id).limit(1))
        c_assigned_to_dev2 = result.scalar_one_or_none()

        if c_assigned_to_dev1:
            print("\n[TEST 3] Agent updating OWN Assigned Complaint...")
            try:
                await complaint_service.update_complaint(
                    c_assigned_to_dev1.complaint_id,
                    c_assigned_to_dev1.org_id,
                    ComplaintUpdate(resolution_notes="Fixed it"),
                    dev1
                )
                print("✅ Success (Expected)")
            except Exception as e:
                print(f"❌ Failed: {e}")
        else:
            print("⚠️ Skipping Test 3 (No complaint assigned to dev1)")

        if c_assigned_to_dev2:
            print("\n[TEST 4] Agent updating OTHER Agent's Complaint...")
            try:
                await complaint_service.update_complaint(
                    c_assigned_to_dev2.complaint_id,
                    c_assigned_to_dev2.org_id,
                    ComplaintUpdate(resolution_notes="Hacked it"),
                    dev1
                )
                print("❌ Success (Unexpected - Should Fail)")
            except AuthorizationError:
                print("✅ Blocked (Expected)")
            except Exception as e:
                print(f"❌ Failed with unexpected error: {e}")
        else:
            print("⚠️ Skipping Test 4 (No complaint assigned to dev2)")
            
        # ==========================================
        # TEST GROUP 3: Agent Pick Up
        # ==========================================
        # Create a new unassigned complaint
        c_new = Complaint(
             org_id=manager.org_id,
             project_id=p1_delivery.project_id,
             subject="Unassigned Issue",
             status=ComplaintStatus.NEW
        )
        db.add(c_new)
        await db.flush()
        
        print("\n[TEST 5] Agent Picking Up Unassigned Complaint...")
        try:
            # Dev1 assigns to self
            await complaint_service.update_complaint(
                c_new.complaint_id,
                c_new.org_id,
                ComplaintUpdate(assign_to_user_id=dev1.user_id),
                dev1
            )
            print("✅ Success (Expected)")
        except Exception as e:
            print(f"❌ Failed: {e}")

        print("\n[TEST 6] Agent Assigning to Someone Else...")
        try:
            # Dev1 tries to assign to Dev2
            await complaint_service.update_complaint(
                c_new.complaint_id,
                c_new.org_id, # Reusing same complaint (now assigned to Dev1, but logic should block regardless of current assignment status for 'assign to other')
                ComplaintUpdate(assign_to_user_id=dev2.user_id),
                dev1
            )
            print("❌ Success (Unexpected - Should Fail)")
        except AuthorizationError:
            print("✅ Blocked (Expected)")
        except Exception as e:
            print(f"❌ Failed with unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(verify_permissions())
