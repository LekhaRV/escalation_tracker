"""
Seed Initial Data
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import AsyncSessionLocal, init_db, engine, Base
from app.models import (
    Organization, User, Project, ProjectTeamMember,
    Complaint, ComplaintCategory, ComplaintAssignment,
    ComplaintInsight, Department
)
from app.core.security import get_password_hash
from app.utils.constants import (
    UserRole, UserStatus, OrgStatus, ProjectStatus,
    ComplaintStatus, SeverityLevel, InsightType, ImpactLevel
)

async def seed_data():
    print("Dropping schema (CASCADE)...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        
    print("Creating tables...")
    await init_db()
    
    async with AsyncSessionLocal() as db:
        print("Seeding data...")
        
        # 1. Create Organization
        org = Organization(
            org_name="Tarento Technologies",
            status=OrgStatus.ACTIVE,
            email_config={"domain": "tarento.com"},
            settings={"sla_thresholds": {"critical": 4, "high": 24}}
        )
        db.add(org)
        await db.flush()

        # 2. Create Departments
        engineering = Department(org_id=org.org_id, name="Engineering")
        delivery = Department(org_id=org.org_id, name="Delivery")
        hr = Department(org_id=org.org_id, name="HR")
        it = Department(org_id=org.org_id, name="IT")

        db.add_all([engineering, delivery, hr, it])
        await db.flush()
        
        # 3. Create Users
        users = []
        # Admin
        admin = User(
            org_id=org.org_id,
            email="admin@tarento.com",
            password=get_password_hash("admin123"),
            name="System Admin",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            department_id=it.department_id
        )
        users.append(admin)
        
        # Manager (Delivery Head)
        manager = User(
            org_id=org.org_id,
            email="manager@tarento.com",
            password=get_password_hash("manager123"),
            name="Project Manager",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
            department_id=delivery.department_id
        )
        users.append(manager)
        
        # Agents (Developers)
        devs = []
        for i in range(5):
            dev = User(
                org_id=org.org_id,
                email=f"dev{i+1}@tarento.com",
                password=get_password_hash("dev123"),
                name=f"Developer {i+1}",
                role=UserRole.AGENT,
                status=UserStatus.ACTIVE,
                department_id=engineering.department_id,
                team="Backend" if i < 3 else "Frontend"
            )
            devs.append(dev)
            users.append(dev)
            
        db.add_all(users)
        await db.flush()

        # Link Managers to Departments
        delivery.manager_id = manager.user_id
        engineering.manager_id = devs[0].user_id # Temporary logic: make dev1 eng lead
        db.add_all([delivery, engineering])
        await db.flush()
        
        # 4. Create Projects
        projects = []
        p1 = Project(
            org_id=org.org_id,
            project_name="E-Gov Platform",
            project_code="EGOV-001",
            client_name="Government of Karnataka",
            description="Unified citizen services platform",
            status=ProjectStatus.ACTIVE,
            project_manager_id=manager.user_id,
            team_lead_id=devs[0].user_id,
            start_date=datetime.now().date(),
            department_id=delivery.department_id
        )
        projects.append(p1)
        
        p2 = Project(
            org_id=org.org_id,
            project_name="FinTech App",
            project_code="FIN-202",
            client_name="Global Bank",
            description="Mobile banking application",
            status=ProjectStatus.ACTIVE,
            project_manager_id=manager.user_id,
            team_lead_id=devs[1].user_id,
            start_date=datetime.now().date(),
            department_id=engineering.department_id
        )
        projects.append(p2)
        
        db.add_all(projects)
        await db.flush()
        
        # 5. Add Team Members
        members = []
        for dev in devs:
            # Add to P1
            m1 = ProjectTeamMember(
                project_id=p1.project_id,
                user_id=dev.user_id,
                role="Developer",
                specialization=["Python", "React"] if "1" in dev.email else ["Java"],
                workload_capacity=10,
                current_workload=random.randint(2, 8),
                is_active=True
            )
            members.append(m1)
            
            # Add some to P2
            if "2" in dev.email or "3" in dev.email:
                m2 = ProjectTeamMember(
                    project_id=p2.project_id,
                    user_id=dev.user_id,
                    role="Developer",
                    specialization=["Flutter"],
                    workload_capacity=10,
                    current_workload=random.randint(1, 5),
                    is_active=True
                )
                members.append(m2)
                
        db.add_all(members)
        await db.flush()
        
        # 5. Create Complaints
        complaints_data = [
            ("Login API failing 500", "Users cannot login to the portal since morning", SeverityLevel.CRITICAL, "technical"),
            ("UI misalignment on mobile", "Dashboard looks broken on iPhone 14", SeverityLevel.LOW, "quality"),
            ("Payment gateway timeout", "Transactions are failing intermittently", SeverityLevel.HIGH, "technical"),
            ("Data export slow", "Exporting reports takes >5 mins", SeverityLevel.MEDIUM, "performance"),
            ("Typo in welcome email", "Says 'Welocme' instead of 'Welcome'", SeverityLevel.LOW, "content")
        ]
        
        for subj, desc, sev, cat_type in complaints_data:
            project = random.choice(projects)
            c = Complaint(
                org_id=org.org_id,
                project_id=project.project_id,
                customer_name="John Customer",
                customer_email="john@example.com",
                subject=subj,
                description=desc,
                status=ComplaintStatus.IN_PROGRESS,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            db.add(c)
            await db.flush()
            
            # Add Category
            cat = ComplaintCategory(
                complaint_id=c.complaint_id,
                category_type=cat_type,
                severity=sev,
                confidence_score=0.95,
                categorized_by="system"
            )
            db.add(cat)
            
            # Add Assignment
            assign = ComplaintAssignment(
                complaint_id=c.complaint_id,
                assigned_to_user_id=random.choice(devs).user_id,
                assignment_reason="Best match",
                sla_deadline=datetime.utcnow() + timedelta(hours=24),
                assigned_by="system"
            )
            db.add(assign)
        
        # 6. Initial Insights
        insight = ComplaintInsight(
            org_id=org.org_id,
            insight_type=InsightType.TREND,
            title="Increasing API Latency",
            description="Login API latency has increased by 15% this week.",
            impact_level=ImpactLevel.HIGH,
            actionable=True
        )
        db.add(insight)
        
        await db.commit()
        print("Seed completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
