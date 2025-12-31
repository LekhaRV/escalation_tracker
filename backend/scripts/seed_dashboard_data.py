
import asyncio
import sys
import os
from datetime import datetime, timedelta
import random
from uuid import uuid4

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models import Complaint, Organization, Project, User, ComplaintCategory, ComplaintAssignment
from app.utils.constants import ComplaintStatus, SeverityLevel
from sqlalchemy import select

async def seed_dashboard_data():
    print("🌱 Seeding dashboard demo data...")
    async with AsyncSessionLocal() as db:
        # Get defaults
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        
        result = await db.execute(select(Project).limit(1))
        project = result.scalars().first()
        
        if not org or not project:
            print("Org or Project missing. Run seed_data.py first.")
            return

        # Create past complaints for trend chart
        complaints_to_add = []
        categories_to_add = []
        
        # Last 7 days distribution
        # Today: already has some
        # Yesterday: 5
        # 2 days ago: 3
        # 3 days ago: 8
        # 4 days ago: 4
        # 5 days ago: 6
        # 6 days ago: 2
        daily_counts = [5, 3, 8, 4, 6, 2]
        
        for i, count in enumerate(daily_counts):
            day_offset = i + 1
            date = datetime.utcnow() - timedelta(days=day_offset)
            
            for _ in range(count):
                c_id = uuid4()
                status = random.choice(list(ComplaintStatus))
                
                complaint = Complaint(
                    complaint_id=c_id,
                    org_id=org.org_id,
                    project_id=project.project_id,
                    customer_email=f"demo{day_offset}_{_}@example.com",
                    subject=f"Historical Complaint {day_offset}-{_}",
                    description="Auto-generated demo data for dashboard trends.",
                    status=status,
                    created_at=date,
                    updated_at=date
                )
                complaints_to_add.append(complaint)
                
                # Add category
                severity = random.choice(list(SeverityLevel))
                cat = ComplaintCategory(
                    complaint_id=c_id,
                    category_type=random.choice(["technical", "billing", "support"]),
                    sub_category="demo",
                    severity=severity,
                    priority=3,
                    department="Support",
                    confidence_score=0.9,
                    categorized_by="seed_script",
                    created_at=date,
                    categorized_at=date
                )
                categories_to_add.append(cat)
        
        db.add_all(complaints_to_add)
        db.add_all(categories_to_add)
        await db.commit()
        print(f"✅ Added {len(complaints_to_add)} historical complaints.")

if __name__ == "__main__":
    asyncio.run(seed_dashboard_data())
