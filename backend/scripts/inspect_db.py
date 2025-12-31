
import asyncio
import sys
import os
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models import Complaint, ComplaintAssignment

from sqlalchemy import func

async def check_complaints():
    print("🔍 Checking recent complaints...")
    async with AsyncSessionLocal() as db:
        count = await db.scalar(select(func.count(Complaint.complaint_id)))
        print(f"Total Complaints: {count}")

        result = await db.execute(
            select(Complaint)
            .options(
                selectinload(Complaint.assignment),
                selectinload(Complaint.category)
            )
            .order_by(desc(Complaint.created_at))
            .limit(3)
        )
        complaints = result.scalars().all()
        
        for c in complaints:
            print(f"---")
            print(f"ID: {c.complaint_id}")
            print(f"Org ID: {c.org_id}")  # Added Org ID check
            print(f"Subject: {c.subject}")
            print(f"Created: {c.created_at}")
            print(f"Status: {c.status}")
            if c.category:
                print(f"Category: {c.category.category_type} (Severity: {c.category.severity})")
                # print(f"   🤖 Reasoning: {c.category.reasoning}") # Column missing
                print(f"   📊 Confidence: {c.category.confidence_score}")
            else:
                print("Category: None")
                
            if c.assignment:
                print(f"Assigned To: {c.assignment.assigned_to_user_id}")
            else:
                print("Assigned To: [Unassigned]")

if __name__ == "__main__":
    asyncio.run(check_complaints())
