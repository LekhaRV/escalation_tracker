
import asyncio
import sys
import os
from sqlalchemy import select, func, text

sys.path.append(os.getcwd())

from app.database import async_session_factory
from app.models import User, ComplaintEscalation, ComplaintAssignment, Complaint

async def verify():
    print("Connecting to DB...")
    async with async_session_factory() as db:
        
        # 1. Check Total Counts
        print("\n--- RAW COUNTS ---")
        esc_count = await db.execute(select(func.count()).select_from(ComplaintEscalation))
        print(f"Total Escalations: {esc_count.scalar()}")

        assign_count = await db.execute(select(func.count()).select_from(ComplaintAssignment))
        print(f"Total Assignments: {assign_count.scalar()}")

        complaint_count = await db.execute(select(func.count()).select_from(Complaint))
        print(f"Total Complaints: {complaint_count.scalar()}")
        
        # 2. Check Specifics
        print("\n--- SAMPLE ESCALATIONS ---")
        escs = await db.execute(select(ComplaintEscalation).limit(5))
        for e in escs.scalars():
            print(f"Escalation To: {e.escalated_to_user_id}")

        print("\n--- SAMPLE ASSIGNMENTS ---")
        assigns = await db.execute(
            select(ComplaintAssignment, Complaint.status)
            .join(Complaint, ComplaintAssignment.complaint_id == Complaint.complaint_id)
            .limit(5)
        )
        for a, status in assigns:
            print(f"Assignment To: {a.assigned_to_user_id}, Status: {status}")

if __name__ == "__main__":
    asyncio.run(verify())
