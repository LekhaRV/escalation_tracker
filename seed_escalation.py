
import asyncio
import sys
import os
from sqlalchemy import select

sys.path.append(os.getcwd())

from app.database import async_session_factory
from app.models import User, Complaint, ComplaintEscalation

async def seed_escalation():
    print("Connecting to DB...")
    async with async_session_factory() as db:
        # 1. Find Admin User
        admin_res = await db.execute(select(User).where(User.email == 'admin@tarento.com'))
        admin = admin_res.scalar_one_or_none()
        if not admin:
            print("Admin not found.")
            return

        # 2. Find a Complaint
        complaint_res = await db.execute(select(Complaint))
        complaint = complaint_res.scalars().first()
        if not complaint:
            print("No complaints found.")
            return

        print(f"Adding escalation for User: {admin.email} on Complaint: {complaint.complaint_id}")

        # 3. Create Escalation
        esc = ComplaintEscalation(
            complaint_id=complaint.complaint_id,
            escalation_level=1,
            escalated_to_user_id=admin.user_id,
            escalation_reason="Test Escalation for Debug",
            escalated_by="system"
        )
        db.add(esc)
        await db.commit()
        print("Escalation seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_escalation())
