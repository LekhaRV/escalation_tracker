"""
Seed Initial Data - Comprehensive Test Data
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
    ComplaintInsight, Department, ComplaintComment
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

        # 2. Create Departments (Tarento-specific)
        delivery = Department(org_id=org.org_id, name="Delivery", description="Project delivery and client management")
        engineering = Department(org_id=org.org_id, name="Engineering", description="Software development and architecture")
        qa = Department(org_id=org.org_id, name="Quality Assurance", description="Testing and quality control")
        devops = Department(org_id=org.org_id, name="DevOps", description="Infrastructure and deployment")
        design = Department(org_id=org.org_id, name="Design", description="UI/UX and product design")
        data_ai = Department(org_id=org.org_id, name="Data & AI", description="Data engineering and machine learning")
        finance = Department(org_id=org.org_id, name="Finance", description="Financial operations")
        hr = Department(org_id=org.org_id, name="HR", description="Human resources and talent")
        client_success = Department(org_id=org.org_id, name="Client Success", description="Customer success and support")

        db.add_all([delivery, engineering, qa, devops, design, data_ai, finance, hr, client_success])
        await db.flush()
        
        # 3. Create Users with Realistic Indian Names
        users = []
        
        # Admin
        admin = User(
            org_id=org.org_id,
            email="admin@tarento.com",
            password=get_password_hash("admin123"),
            name="System Admin",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            department_id=devops.department_id
        )
        users.append(admin)
        
        # Manager (Delivery Head)
        manager = User(
            org_id=org.org_id,
            email="manager@tarento.com",
            password=get_password_hash("manager123"),
            name="Priya Sharma",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
            department_id=delivery.department_id
        )
        users.append(manager)
        
        # Engineering Manager
        eng_manager = User(
            org_id=org.org_id,
            email="engmanager@tarento.com",
            password=get_password_hash("manager123"),
            name="Rajesh Kumar",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
            department_id=engineering.department_id
        )
        users.append(eng_manager)
        
        # Developers with realistic names
        dev_names = [
            ("Arjun Patel", "arjun@tarento.com", "Backend"),
            ("Sneha Reddy", "sneha@tarento.com", "Backend"),
            ("Vikram Singh", "vikram@tarento.com", "Backend"),
            ("Ananya Iyer", "ananya@tarento.com", "Frontend"),
            ("Rohan Gupta", "rohan@tarento.com", "Frontend"),
            ("Kavitha Nair", "kavitha@tarento.com", "Fullstack"),
            ("Amit Joshi", "amit@tarento.com", "Fullstack"),
        ]
        
        devs = []
        for name, email, team in dev_names:
            dev = User(
                org_id=org.org_id,
                email=email,
                password=get_password_hash("dev123"),
                name=name,
                role=UserRole.AGENT,
                status=UserStatus.ACTIVE,
                department_id=engineering.department_id,
                team=team
            )
            devs.append(dev)
            users.append(dev)
        
        # QA Engineers
        qa_names = [
            ("Meera Krishnan", "meera@tarento.com"),
            ("Suresh Babu", "suresh@tarento.com"),
        ]
        qa_users = []
        for name, email in qa_names:
            qa_user = User(
                org_id=org.org_id,
                email=email,
                password=get_password_hash("dev123"),
                name=name,
                role=UserRole.AGENT,
                status=UserStatus.ACTIVE,
                department_id=qa.department_id,
                team="QA"
            )
            qa_users.append(qa_user)
            users.append(qa_user)
        
        # DevOps Engineer
        devops_user = User(
            org_id=org.org_id,
            email="deepak@tarento.com",
            password=get_password_hash("dev123"),
            name="Deepak Menon",
            role=UserRole.AGENT,
            status=UserStatus.ACTIVE,
            department_id=devops.department_id,
            team="DevOps"
        )
        users.append(devops_user)
        
        # Viewer (Stakeholder)
        viewer = User(
            org_id=org.org_id,
            email="viewer@tarento.com",
            password=get_password_hash("viewer123"),
            name="Lakshmi Venkatesh",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
            department_id=client_success.department_id
        )
        users.append(viewer)
            
        db.add_all(users)
        await db.flush()

        # Link Managers to Departments
        delivery.manager_id = manager.user_id
        engineering.manager_id = eng_manager.user_id
        db.add_all([delivery, engineering])
        await db.flush()
        
        # 4. Create Projects
        projects = []
        p1 = Project(
            org_id=org.org_id,
            project_name="E-Gov Platform",
            project_code="EGOV-001",
            client_name="Government of Karnataka",
            description="Unified citizen services platform for Karnataka state",
            status=ProjectStatus.ACTIVE,
            project_manager_id=manager.user_id,
            team_lead_id=devs[0].user_id,
            start_date=datetime.now().date() - timedelta(days=90)
        )
        projects.append(p1)
        
        p2 = Project(
            org_id=org.org_id,
            project_name="FinTech App",
            project_code="FIN-202",
            client_name="Global Bank",
            description="Mobile banking application with AI fraud detection",
            status=ProjectStatus.ACTIVE,
            project_manager_id=manager.user_id,
            team_lead_id=devs[1].user_id,
            start_date=datetime.now().date() - timedelta(days=60)
        )
        projects.append(p2)
        
        p3 = Project(
            org_id=org.org_id,
            project_name="HealthTech Portal",
            project_code="HEALTH-303",
            client_name="Apollo Hospitals",
            description="Patient management and telemedicine platform",
            status=ProjectStatus.ACTIVE,
            project_manager_id=eng_manager.user_id,
            team_lead_id=devs[2].user_id,
            start_date=datetime.now().date() - timedelta(days=30)
        )
        projects.append(p3)
        
        db.add_all(projects)
        await db.flush()
        
        # 5. Add Team Members to Projects
        members = []
        
        # E-Gov Platform team
        for dev in devs[:4]:
            members.append(ProjectTeamMember(
                project_id=p1.project_id,
                user_id=dev.user_id,
                role="Developer",
                specialization=["Python", "React", "PostgreSQL"],
                workload_capacity=10,
                current_workload=random.randint(3, 8),
                is_active=True
            ))
        members.append(ProjectTeamMember(
            project_id=p1.project_id,
            user_id=qa_users[0].user_id,
            role="QA Lead",
            specialization=["Selenium", "API Testing"],
            workload_capacity=8,
            current_workload=5,
            is_active=True
        ))
        
        # FinTech App team
        for dev in devs[2:6]:
            members.append(ProjectTeamMember(
                project_id=p2.project_id,
                user_id=dev.user_id,
                role="Developer",
                specialization=["Flutter", "Dart", "Firebase"],
                workload_capacity=10,
                current_workload=random.randint(2, 6),
                is_active=True
            ))
        
        # HealthTech team
        for dev in devs[4:7]:
            members.append(ProjectTeamMember(
                project_id=p3.project_id,
                user_id=dev.user_id,
                role="Developer",
                specialization=["Node.js", "Vue.js", "MongoDB"],
                workload_capacity=10,
                current_workload=random.randint(1, 5),
                is_active=True
            ))
        members.append(ProjectTeamMember(
            project_id=p3.project_id,
            user_id=qa_users[1].user_id,
            role="QA Engineer",
            specialization=["Manual Testing", "Cypress"],
            workload_capacity=8,
            current_workload=4,
            is_active=True
        ))
                
        db.add_all(members)
        await db.flush()
        
        # 6. Create Complaints with Various Statuses
        complaints_data = [
            # Critical - New
            ("Login API returning 500 errors", "Production login is completely down since 6 AM. Users cannot access their accounts.", SeverityLevel.CRITICAL, "technical", ComplaintStatus.NEW, None, "Ramesh Kumar", "ramesh@customer.com", p1),
            
            # High - In Progress
            ("Payment gateway timeout", "Payment transactions are failing with timeout errors. Approximately 30% failure rate.", SeverityLevel.HIGH, "technical", ComplaintStatus.IN_PROGRESS, devs[1], "Sanjay Mehta", "sanjay@globalbank.com", p2),
            
            # Medium - In Progress
            ("Dashboard charts not loading on mobile", "The analytics dashboard charts are not rendering properly on iOS Safari.", SeverityLevel.MEDIUM, "quality", ComplaintStatus.IN_PROGRESS, devs[3], "Dr. Anil Shah", "anil.shah@apollo.com", p3),
            
            # Low - Resolved
            ("Typo in welcome email", "The welcome email says 'Welocme' instead of 'Welcome'.", SeverityLevel.LOW, "content", ComplaintStatus.RESOLVED, devs[4], "Priyanka Das", "priyanka@example.com", p1),
            
            # High - New
            ("Data export taking >10 minutes", "Exporting more than 1000 records causes the browser to freeze.", SeverityLevel.HIGH, "performance", ComplaintStatus.NEW, None, "Vijay Malhotra", "vijay@karnataka.gov.in", p1),
            
            # Medium - In Progress
            ("OTP not being received", "Users in Tier-2 cities are not receiving OTP SMS.", SeverityLevel.MEDIUM, "technical", ComplaintStatus.IN_PROGRESS, devs[5], "Sunita Rao", "sunita@globalbank.com", p2),
            
            # Critical - In Progress
            ("Database connection pool exhausted", "Application throwing 'too many connections' error during peak hours.", SeverityLevel.CRITICAL, "technical", ComplaintStatus.IN_PROGRESS, devops_user, "Arun Krishnamurthy", "arun@karnataka.gov.in", p1),
            
            # Low - Resolved
            ("Profile picture upload failing", "Users cannot upload profile pictures larger than 2MB.", SeverityLevel.LOW, "technical", ComplaintStatus.RESOLVED, devs[6], "Neha Agarwal", "neha@apollo.com", p3),
            
            # Medium - New
            ("Search results not accurate", "Search for patient names returns unrelated results sometimes.", SeverityLevel.MEDIUM, "quality", ComplaintStatus.NEW, None, "Dr. Rekha Iyer", "rekha@apollo.com", p3),
            
            # High - In Progress
            ("SSL certificate expiring", "SSL certificate for production domain expires in 3 days.", SeverityLevel.HIGH, "technical", ComplaintStatus.IN_PROGRESS, devops_user, "IT Team", "it@tarento.com", p2),
        ]
        
        created_complaints = []
        for subj, desc, sev, cat_type, status, assigned_to, cust_name, cust_email, project in complaints_data:
            hours_ago = random.randint(2, 120)
            c = Complaint(
                org_id=org.org_id,
                project_id=project.project_id,
                customer_name=cust_name,
                customer_email=cust_email,
                subject=subj,
                description=desc,
                status=status,
                created_at=datetime.utcnow() - timedelta(hours=hours_ago),
                resolved_at=datetime.utcnow() if status == ComplaintStatus.RESOLVED else None,
                resolution_notes="Issue fixed and deployed to production." if status == ComplaintStatus.RESOLVED else None
            )
            db.add(c)
            await db.flush()
            created_complaints.append((c, assigned_to, sev, cat_type))
            
            # Add Category
            cat = ComplaintCategory(
                complaint_id=c.complaint_id,
                category_type=cat_type,
                severity=sev,
                confidence_score=0.92 + random.random() * 0.07,
                categorized_by="ai"
            )
            db.add(cat)
            
            # Add Assignment if assigned
            if assigned_to:
                sla_hours = {SeverityLevel.CRITICAL: 4, SeverityLevel.HIGH: 24, SeverityLevel.MEDIUM: 72, SeverityLevel.LOW: 168}
                assign = ComplaintAssignment(
                    complaint_id=c.complaint_id,
                    assigned_to_user_id=assigned_to.user_id,
                    assignment_reason="AI-based skill matching",
                    sla_deadline=c.created_at + timedelta(hours=sla_hours.get(sev, 72)),
                    assigned_by="system"
                )
                db.add(assign)
        
        await db.flush()
        
        # 6.5 Add EXTRA complaints to trigger AI insights for demo
        print("Adding extra complaints for AI insight triggers...")
        
        # FOR TOP PERFORMER: Give devs[0] (Arjun Patel) 5 resolved complaints
        top_performer_agent = devs[0]  # Arjun Patel
        for i in range(5):
            c = Complaint(
                org_id=org.org_id,
                project_id=random.choice(projects).project_id,
                customer_name=f"Customer {i + 100}",
                customer_email=f"customer{i + 100}@example.com",
                subject=f"Issue resolved by top agent #{i + 1}",
                description=f"This was efficiently resolved by {top_performer_agent.name}",
                status=ComplaintStatus.RESOLVED,
                created_at=datetime.utcnow() - timedelta(days=random.randint(3, 10)),
                resolved_at=datetime.utcnow() - timedelta(days=random.randint(1, 2)),
                resolution_notes="Resolved quickly by top performer."
            )
            db.add(c)
            await db.flush()
            
            cat = ComplaintCategory(
                complaint_id=c.complaint_id,
                category_type="technical",
                severity=random.choice([SeverityLevel.MEDIUM, SeverityLevel.HIGH]),
                confidence_score=0.95,
                categorized_by="ai"
            )
            db.add(cat)
            
            assign = ComplaintAssignment(
                complaint_id=c.complaint_id,
                assigned_to_user_id=top_performer_agent.user_id,
                assignment_reason="Top performer assignment",
                sla_deadline=c.created_at + timedelta(hours=72),
                assigned_by="system"
            )
            db.add(assign)
        
        # FOR ANOMALY DETECTION: Create spike of complaints yesterday
        yesterday = datetime.utcnow().replace(hour=14, minute=0, second=0, microsecond=0) - timedelta(days=1)
        for i in range(8):  # 8 complaints yesterday = spike above 14-day average
            c = Complaint(
                org_id=org.org_id,
                project_id=random.choice(projects).project_id,
                customer_name=f"Spike Customer {i + 200}",
                customer_email=f"spike{i + 200}@example.com",
                subject=f"Unusual spike complaint #{i + 1}",
                description="Part of yesterday's unusual complaint spike",
                status=random.choice([ComplaintStatus.NEW, ComplaintStatus.IN_PROGRESS]),
                created_at=yesterday + timedelta(hours=random.randint(0, 10)),
            )
            db.add(c)
            await db.flush()
            
            cat = ComplaintCategory(
                complaint_id=c.complaint_id,
                category_type="technical",
                severity=random.choice([SeverityLevel.MEDIUM, SeverityLevel.HIGH]),
                confidence_score=0.90,
                categorized_by="ai"
            )
            db.add(cat)
            
            if random.random() > 0.3:  # 70% assigned
                assign = ComplaintAssignment(
                    complaint_id=c.complaint_id,
                    assigned_to_user_id=random.choice(devs).user_id,
                    assignment_reason="Spike complaint assignment",
                    sla_deadline=c.created_at + timedelta(hours=48),
                    assigned_by="system"
                )
                db.add(assign)
        
        await db.flush()
        print("✅ Extra complaints added for AI insights demo (Top Performer + Anomaly)")
        
        # 7. Add Comments to Some Complaints
        comments_data = [
            (created_complaints[1][0], devs[1], "Investigating the payment gateway logs. Found some timeout patterns."),
            (created_complaints[1][0], manager, "Please prioritize this. Client escalated to VP level."),
            (created_complaints[1][0], devs[1], "Root cause identified - connection pool size too small. Deploying fix."),
            (created_complaints[2][0], devs[3], "Tested on iOS 16.4 Safari. The issue is with Chart.js version."),
            (created_complaints[2][0], qa_users[0], "Confirmed. Upgrading to Chart.js 4.x should fix this."),
            (created_complaints[6][0], devops_user, "Increased max_connections from 100 to 200. Monitoring."),
            (created_complaints[6][0], eng_manager, "Let's also look at connection pooling at app level."),
        ]
        
        for complaint, user, content in comments_data:
            comment = ComplaintComment(
                complaint_id=complaint.complaint_id,
                user_id=user.user_id,
                content=content,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            )
            db.add(comment)
        
        # 8. Create Insights
        insights = [
            (InsightType.TREND, "Increasing API Latency", "Login API latency has increased by 35% this week. Consider scaling the auth service.", ImpactLevel.HIGH),
            (InsightType.ALERT, "Recurring Payment Failures", "Payment gateway timeouts occur mainly between 6-8 PM IST. Correlates with peak traffic.", ImpactLevel.HIGH),
            (InsightType.ALERT, "Unusual Error Spike", "Error rate spiked 300% on Monday. Related to deployment at 2 PM.", ImpactLevel.MEDIUM),
            (InsightType.RECOMMENDATION, "Enable Caching", "Enabling Redis caching for dashboard queries could reduce load by 60%.", ImpactLevel.MEDIUM),
            (InsightType.TREND, "Mobile Issues Increasing", "40% of bugs reported are mobile-specific. Consider dedicated mobile QA.", ImpactLevel.LOW),
        ]
        
        for insight_type, title, desc, impact in insights:
            insight = ComplaintInsight(
                org_id=org.org_id,
                insight_type=insight_type,
                title=title,
                description=desc,
                impact_level=impact,
                actionable=True
            )
            db.add(insight)
        
        await db.commit()
        print("✅ Seed completed successfully!")
        print(f"   - {len(users)} users created")
        print(f"   - {len(projects)} projects created")
        print(f"   - {len(created_complaints)} complaints created")
        print(f"   - {len(comments_data)} comments added")
        print(f"   - {len(insights)} insights generated")

if __name__ == "__main__":
    asyncio.run(seed_data())
