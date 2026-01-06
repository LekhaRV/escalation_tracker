
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, select
from app.database import AsyncSessionLocal
from app.models import User, ComplaintAssignment, Complaint

async def debug_workload():
    async with AsyncSessionLocal() as db:
        print("--- Debugging Workload ---")
        
        # 1. Start with assignments
        result = await db.execute(select(ComplaintAssignment))
        assignments = result.scalars().all()
        print(f"Total Assignments: {len(assignments)}")
        
        for a in assignments[:5]:
            print(f"  AssignID: {a.assignment_id}, UserID: {a.assigned_to_user_id}, ComplaintID: {a.complaint_id}")
            
        # 2. Check Active Complaints
        result = await db.execute(select(Complaint).where(Complaint.status.in_(['NEW', 'IN_PROGRESS'])))
        active_complaints = result.scalars().all()
        print(f"Total Active Complaints: {len(active_complaints)}")
        
        # 3. Check Join Logic (mimic analytics_service)
        # Count active complaints per user
        stmt = text("""
            SELECT u.name, COUNT(c.complaint_id) as active_count
            FROM users u
            LEFT JOIN complaint_assignments ca ON u.user_id = ca.assigned_to_user_id
            LEFT JOIN complaints c ON ca.complaint_id = c.complaint_id 
                AND c.status IN ('NEW', 'IN_PROGRESS')
            WHERE u.role IN ('AGENT', 'ADMIN', 'MANAGER') AND u.status = 'ACTIVE'
            GROUP BY u.user_id, u.name
        """)
        
        result = await db.execute(stmt)
        rows = result.all()
        print("\n--- Workload Query Result ---")
        for row in rows:
            print(f"User: {row.name}, Active Count: {row.active_count}")

if __name__ == "__main__":
    asyncio.run(debug_workload())
