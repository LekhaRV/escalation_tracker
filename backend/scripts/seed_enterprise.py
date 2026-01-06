
import asyncio
import os
import sys
import random
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path to allow importing app modules
import sys
import os
sys.path.insert(0, "/app")  # Docker container path priority
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Local path fallback

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import (
    User, Organization, Department, Project, ProjectTeamMember,
    Complaint, ComplaintCategory, ComplaintAssignment, ComplaintEscalation,
    ComplaintInsight
)
from app.utils.constants import (
    UserRole, UserStatus, ComplaintStatus, SeverityLevel,
    InsightType, PatternType
)
from app.utils.security import get_password_hash

# Setup Database
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# CONSTANTS
DEPARTMENTS = [
    "Engineering", "Product", "Design", "Sales", "Support", 
    "Marketing", "HR", "Finance", "Legal", "Operations"
]

PROJECT_NAMES = [
    "Alpha Migration", "Beta Launch", "Omega Redesign", "Project Phoenix",
    "Cloud Native Transformation", "Legacy Retirement", "Mobile App v2",
    "Data Lake Implementation", "AI Integration", "Security Audit Fixes",
    "Customer Portal", "Internal Tools", "Billing System Upgrade",
    "API Gateway", "Microservices Split", "Frontend Revamp",
    "Blockchain Pilot", "IoT Platform", "Analytics Dashboard", "Search Engine"
]

CLIENTS = [
    "Acme Corp", "Globex", "Soylent Corp", "Initech", "Umbrella Corp",
    "Wayne Enterprises", "Stark Industries", "Cyberdyne", "Massive Dynamic"
]

COMPLAINT_SUBJECTS = [
    "Login failing with 500 error", "Dashboard slow to load", "API timeout on /users",
    "Mobile app crashes on startup", "Data missing from export", "Billing amount incorrect",
    "Cannot invite new members", "Email notifications not sending", "SSO integration broken",
    "Search returns zero results", "Upload button disabled", "Dark mode glitch",
    "Permission denied on public page", "Payment gateway rejected card", "Invoice PDF blank",
    "Password reset link expired", "Two-factor auth loop", "Latency in EU region",
    "Memory leak in worker node", "Database connection pool exhausted"
]

def random_date(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )

async def seed_enterprise():
    async with AsyncSessionLocal() as db:
        print("🌱 Starting Enterprise Seeding...")
        
        # 1. Create Organization
        org_id = uuid4()
        org = Organization(
            org_id=org_id,
            name="Traxion Enterprise",
            subscription_plan="enterprise",
            domain="traxion.ai"
        )
        db.add(org)
        await db.flush()
        print(f"✅ Organization created: {org.name}")

        # 2. Create Departments
        depts = []
        for name in DEPARTMENTS:
            d = Department(
                org_id=org_id,
                name=name,
                description=f"The {name} department handles all {name.lower()}-related activities."
            )
            db.add(d)
            depts.append(d)
        await db.flush()
        print(f"✅ {len(depts)} Departments created")

        # 3. Create Users (50 total)
        users = []
        # Admin
        admin = User(
            org_id=org_id,
            email="admin@traxion.ai",
            password=get_password_hash("password123"),
            name="System Admin",
            role=UserRole.ADMIN,
            department_id=depts[0].department_id, # Eng
            status=UserStatus.ACTIVE
        )
        db.add(admin)
        users.append(admin)

        # Managers (1 per dept)
        managers = []
        for d in depts:
            m = User(
                org_id=org_id,
                email=f"manager.{d.name.lower()}@traxion.ai",
                password=get_password_hash("password123"),
                name=f"{d.name} Manager",
                role=UserRole.MANAGER,
                department_id=d.department_id,
                status=UserStatus.ACTIVE
            )
            db.add(m)
            managers.append(m)
            users.append(m)
            # Link manager to dept
            d.manager_id = m.user_id

        # Agents (4 per dept)
        agents = []
        first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        for d in depts:
            for i in range(4):
                fn = random.choice(first_names)
                ln = random.choice(last_names)
                u = User(
                    org_id=org_id,
                    email=f"{fn.lower()}.{ln.lower()}{random.randint(1,99)}@traxion.ai",
                    password=get_password_hash("password123"),
                    name=f"{fn} {ln}",
                    role=UserRole.AGENT,
                    department_id=d.department_id,
                    status=UserStatus.ACTIVE
                )
                db.add(u)
                agents.append(u)
                users.append(u)

        await db.flush()
        print(f"✅ {len(users)} Users created")

        # 4. Create Projects
        projects = []
        eng_dept_id = next(d.department_id for d in depts if d.name == "Engineering")
        eng_manager_id = next(u.user_id for u in managers if u.department_id == eng_dept_id)

        for pname in PROJECT_NAMES:
            p = Project(
                org_id=org_id,
                project_name=pname,
                client_name=random.choice(CLIENTS),
                description=f"Enterprise initiative for {pname}",
                project_manager_id=eng_manager_id,
                team_lead_id=random.choice(agents).user_id, # Random agent as lead
                status="active",
                department_id=eng_dept_id
            )
            db.add(p)
            projects.append(p)
        
        await db.flush()
        
        # Add Team Members to Projects
        for p in projects:
            # Add 3-5 random agents to each project
            team = random.sample(agents, k=random.randint(3, 5))
            for member in team:
                ptm = ProjectTeamMember(
                    project_id=p.project_id,
                    user_id=member.user_id,
                    role="Developer",
                    current_workload=0,
                    workload_capacity=10
                )
                db.add(ptm)
        
        await db.flush()
        print(f"✅ {len(projects)} Projects created with teams")

        # 5. Create Complaints (200)
        complaints = []
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()

        for i in range(200):
            created_at = random_date(start_date, end_date)
            status = random.choices(
                [ComplaintStatus.NEW, ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED], 
                weights=[10, 30, 60], k=1
            )[0]
            
            proj = random.choice(projects)
            subj = random.choice(COMPLAINT_SUBJECTS)
            
            c = Complaint(
                org_id=org_id,
                project_id=proj.project_id,
                customer_name=f"Customer {i}",
                customer_email=f"customer{i}@{proj.client_name.lower().replace(' ', '')}.com",
                subject=subj,
                description=f"Detailed description regarding {subj}. Please investigate.",
                status=status,
                created_at=created_at,
                updated_at=created_at
            )
            
            if status == ComplaintStatus.RESOLVED:
                c.resolved_at = created_at + timedelta(hours=random.randint(2, 48))
            
            db.add(c)
            await db.flush() # Need ID
            
            # Category
            sev = random.choices(
                [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL],
                weights=[20, 50, 20, 10], k=1
            )[0]
            
            cat = ComplaintCategory(
                complaint_id=c.complaint_id,
                category_type="Technical",
                sub_category="Bug",
                severity=sev,
                confidence_score=0.95,
                categorized_at=created_at + timedelta(minutes=2)
            )
            db.add(cat)

            # Assignment
            assignee = random.choice(agents)
            assign = ComplaintAssignment(
                complaint_id=c.complaint_id,
                assigned_to_user_id=assignee.user_id,
                assignment_reason="Workload Balancing",
                assigned_by="system",
                assigned_at=created_at + timedelta(minutes=5),
                sla_deadline=created_at + timedelta(hours=24)
            )
            db.add(assign)

            # Update workload if active
            if status != ComplaintStatus.RESOLVED:
                # Need to update ProjectTeamMember logic? 
                # For seeding just assuming DB query calculates it dynamically as per my recent fix.
                pass

        await db.commit()
        print(f"✅ 200 Complaints created")
        print("🌱 Seeding Complete!")

if __name__ == "__main__":
    asyncio.run(seed_enterprise())
