
import asyncio
import sys
import os
from datetime import datetime, timedelta
import random
from uuid import uuid4

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models import Complaint, Organization, Project, User, ComplaintCategory, ComplaintAssignment, ComplaintPattern, ComplaintInsight
from app.utils.constants import ComplaintStatus, SeverityLevel
from sqlalchemy import select, delete

async def super_seed():
    print("🧨 SUPER SEED: Clearing old data and creating dense history...")
    async with AsyncSessionLocal() as db:
        # Get org
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        result = await db.execute(select(Project).limit(1))
        project = result.scalars().first()
        
        if not org or not project:
            print("Org missing")
            return

        # 1. Clear existing complaints to avoid duplicates/confusion
        print("   - Clearing complaints...")
        await db.execute(delete(Complaint).where(Complaint.org_id == org.org_id))
        await db.execute(delete(ComplaintPattern).where(ComplaintPattern.org_id == org.org_id))
        await db.execute(delete(ComplaintInsight).where(ComplaintInsight.org_id == org.org_id))
        
        # 2. Add 30 days of data
        print("   - Generating 30 days of data...")
        complaints_to_add = []
        categories_to_add = []
        
        # Trend shape: Increasing then decreasing
        trend_shape = [2, 3, 5, 2, 4, 6, 8, 12, 15, 10, 8, 12, 14, 18, 20, 22, 15, 12, 8, 5, 4, 6, 8, 10, 12, 15, 8, 4, 2, 1]
        
        now = datetime.utcnow()
        
        # Get Admin user to assign to
        result = await db.execute(select(User).where(User.email == "admin@tarento.com"))
        assignee = result.scalars().first()
        assignments_to_add = []

        for i, count in enumerate(trend_shape):
            # i=0 is 30 days ago
            day_offset = 30 - i
            date = now - timedelta(days=day_offset)
            
            for _ in range(count):
                c_id = uuid4()
                status = random.choice(list(ComplaintStatus))
                
                complaint = Complaint(
                    complaint_id=c_id,
                    org_id=org.org_id,
                    project_id=project.project_id,
                    customer_email=f"user{i}_{_}@example.com",
                    subject=f"Complaint from {date.strftime('%Y-%m-%d')}",
                    description=f"Automated complaint description for day {day_offset}",
                    status=status,
                    created_at=date,
                    updated_at=date
                )
                complaints_to_add.append(complaint)
                
                # Category
                cat = ComplaintCategory(
                    complaint_id=c_id,
                    category_type=random.choice(["technical", "billing", "support"]),
                    sub_category="service",
                    severity=random.choice(list(SeverityLevel)),
                    priority=3,
                    department="Support",
                    confidence_score=0.95,
                    categorized_by="super_seed",
                    created_at=date,
                    categorized_at=date
                )
                categories_to_add.append(cat)
                
                # Assignment (80% chance)
                if assignee and random.random() > 0.2:
                    complaint.status = ComplaintStatus.IN_PROGRESS
                    assignment = ComplaintAssignment(
                        complaint_id=c_id,
                        user_id=assignee.user_id,
                        status="assigned",
                        assigned_at=date,
                        sla_deadline=date + timedelta(hours=24)
                    )
                    assignments_to_add.append(assignment)
        
        db.add_all(complaints_to_add)
        db.add_all(categories_to_add)
        db.add_all(assignments_to_add)
        await db.commit()
        print(f"✅ Added {len(complaints_to_add)} complaints over 30 days ({len(assignments_to_add)} assigned).")

if __name__ == "__main__":
    asyncio.run(super_seed())
