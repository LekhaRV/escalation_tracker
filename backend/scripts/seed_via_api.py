
import requests
import random
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com" # Default in many setups, will try others if fails
ADMIN_PASSWORD = "password"

# Data Pools
DEPARTMENTS = ["Engineering", "Product", "Sales", "Support", "Marketing", "HR", "Finance", "Legal"]
FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
COMPLAINT_SUBJECTS = [
    "Login failing with 500 error", "Dashboard slow to load", "API timeout on /users",
    "Mobile app crashes on startup", "Data missing from export", "Billing amount incorrect",
    "Cannot invite new members", "Email notifications not sending", "SSO integration broken",
    "Search returns zero results"
]

def get_token():
    # Try standard credentials
    creds_list = [
        ("admin@example.com", "password"),
        ("admin@traxion.ai", "password123"),
        ("user@example.com", "password")
    ]
    
    for email, pwd in creds_list:
        try:
            print(f"Trying login with {email}...")
            resp = requests.post(f"http://localhost:8000/api/v1/login/access-token", data={
                "username": email,
                "password": pwd
            })
            if resp.status_code == 200:
                print(f"✅ Login successful as {email}")
                return resp.json()["access_token"]
        except Exception as e:
            print(f"Connection error: {e}")
    
    print("❌ Could not login. Make sure the backend is running and an admin user exists.")
    return None

def seed_data():
    token = get_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Users (Agents)
    print("Creating users...")
    users = []
    for i in range(20):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(100,999)}@traxion.ai"
        
        user_data = {
            "email": email,
            "password": "password123",
            "name": f"{fn} {ln}",
            "role": "agent",
            "is_active": True
        }
        
        # Check if exists (optimization: just try create and ignore 400)
        resp = requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers)
        if resp.status_code in [200, 201]:
            users.append(resp.json())
            print(f"  + Created user {email}")
        else:
            print(f"  - Failed/Exists {email}: {resp.status_code}")

    # 2. Create Complaints
    print("Creating complaints...")
    for i in range(50):
        subj = random.choice(COMPLAINT_SUBJECTS)
        severity = random.choice(["low", "medium", "high", "critical"])
        
        complaint_data = {
            "subject": subj,
            "description": f"Detailed description for {subj}. This issue has been persisting for {random.randint(1, 48)} hours.",
            "customer_name": f"Customer {i}",
            "customer_email": f"customer{i}@client.com",
            "severity": severity,
            "product": "Traxion Cloud",
            "status": "new"
        }
        
        resp = requests.post(f"{BASE_URL}/complaints/", json=complaint_data, headers=headers)
        if resp.status_code in [200, 201]:
            c_id = resp.json()["complaint_id"]
            print(f"  + Created complaint {c_id[:8]}...")
            
            # Simple simulation of handling
            if random.random() > 0.3:
                # Assign to random user (if we have users list, or just leave it)
                # This script assumes the user running it (admin) can assign.
                pass
                
        else:
            print(f"  - Failed complaint: {resp.text}")

    print("✅ Seeding Complete")

if __name__ == "__main__":
    seed_data()
