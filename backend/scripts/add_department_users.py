"""
Script to add users for all departments to enable proper complaint routing.
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.organization import Organization
from app.models.user import User
from app.utils.constants import UserRole, UserStatus

# Users to add for each department
NEW_USERS = [
    # Finance Team
    {"name": "Finance Lead", "email": "finance.lead@tarento.com", "department": "Finance", "role": UserRole.MANAGER, "team": "Finance"},
    {"name": "Finance Analyst", "email": "finance.analyst@tarento.com", "department": "Finance", "role": UserRole.AGENT, "team": "Finance"},
    
    # Support Team  
    {"name": "Support Manager", "email": "support.manager@tarento.com", "department": "Support", "role": UserRole.MANAGER, "team": "Support"},
    {"name": "Support Agent 1", "email": "support.agent1@tarento.com", "department": "Support", "role": UserRole.AGENT, "team": "Support"},
    {"name": "Support Agent 2", "email": "support.agent2@tarento.com", "department": "Support", "role": UserRole.AGENT, "team": "Support"},
    
    # Account Management
    {"name": "Account Director", "email": "account.director@tarento.com", "department": "Account Management", "role": UserRole.MANAGER, "team": "Accounts"},
    {"name": "Account Manager 1", "email": "account.manager1@tarento.com", "department": "Account Management", "role": UserRole.AGENT, "team": "Accounts"},
    
    # Quality Assurance
    {"name": "QA Lead", "email": "qa.lead@tarento.com", "department": "Quality Assurance", "role": UserRole.MANAGER, "team": "QA"},
    {"name": "QA Engineer 1", "email": "qa.engineer1@tarento.com", "department": "Quality Assurance", "role": UserRole.AGENT, "team": "QA"},
    {"name": "QA Engineer 2", "email": "qa.engineer2@tarento.com", "department": "Quality Assurance", "role": UserRole.AGENT, "team": "QA"},
    
    # Project Management (distinct from Delivery)
    {"name": "Senior PM", "email": "senior.pm@tarento.com", "department": "Project Management", "role": UserRole.MANAGER, "team": "PMO"},
    {"name": "Project Coordinator", "email": "project.coordinator@tarento.com", "department": "Project Management", "role": UserRole.AGENT, "team": "PMO"},
    
    # Resource Management
    {"name": "Resource Manager", "email": "resource.manager@tarento.com", "department": "Resource Management", "role": UserRole.MANAGER, "team": "HR"},
]

async def add_users():
    print("🚀 Adding department users for efficient routing...")
    
    async with AsyncSessionLocal() as db:
        # Get org
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        
        if not org:
            print("❌ No Organization found.")
            return
        
        created = 0
        skipped = 0
        
        for user_data in NEW_USERS:
            # Check if user exists
            existing = await db.execute(
                select(User).where(User.email == user_data["email"])
            )
            if existing.scalar_one_or_none():
                print(f"   ⏭️  Skipping {user_data['name']} (already exists)")
                skipped += 1
                continue
            
            user = User(
                org_id=org.org_id,
                email=user_data["email"],
                password="$2b$12$placeholder",  # Hashed placeholder
                name=user_data["name"],
                role=user_data["role"],
                team=user_data["team"],
                department=user_data["department"],
                status=UserStatus.ACTIVE
            )
            db.add(user)
            created += 1
            print(f"   ✅ Created: {user_data['name']} ({user_data['department']})")
        
        await db.commit()
        
        print(f"\n📊 Summary: Created {created}, Skipped {skipped}")
        
        # Show final department counts
        print("\n=== Department Roster ===")
        result = await db.execute(select(User))
        users = result.scalars().all()
        depts = {}
        for u in users:
            dept = u.department or "None"
            depts[dept] = depts.get(dept, 0) + 1
        for dept, count in sorted(depts.items()):
            print(f"   {dept}: {count} users")

if __name__ == "__main__":
    asyncio.run(add_users())
