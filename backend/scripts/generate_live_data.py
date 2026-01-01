
import asyncio
import sys
import os
import random

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.email_service import email_service

SCENARIOS = [
    {
        "sender": "John Smith <john.smith@karnataka.gov.in>",
        "subject": "CRITICAL: E-Gov Portal 500 Errors affecting citizens",
        "content": "We are receiving widespread reports of 500 Internal Server Errors on the tax payment gateway. This is blocking revenue collection. Start immediate investigation. The logs show timeouts connecting to the payment switch."
    },
    {
        "sender": "Sarah Jones <s.jones@globalbank.com>",
        "subject": "Mobile App Crash on iOS 17",
        "content": "The latest build of the FinTech app is crashing immediately on launch for all users on iOS 17.4. We need a hotfix deployed today. This is a blocker for the marketing campaign launching tomorrow."
    },
    {
        "sender": "Mike Ross <mike@startuphub.com>",
        "subject": "Billing Discrepancy in invoice #4402",
        "content": "Hi team, I noticed we were charged for 400 hours of development but the timesheets only show 350. Can someone from the accounts team please clarify this discrepancy before we process payment?"
    },
    {
        "sender": "Priya Sharma <priya@retail-giant.com>",
        "subject": "Feature Request: Export to PDF",
        "content": "Our operations team really needs the ability to export the weekly sales report to PDF. Currently CSV is the only option and the formatting gets messed up when they print it. Is this something we can add to the next sprint?"
    },
    {
        "sender": "Ops Alert <alerts@monitoring.com>",
        "subject": "Security Alert: Suspicious SQL Injection attempts",
        "content": "WAF has detected 5000+ SQL injection attempts from IP 104.22.11.1 targeting the login endpoint /api/v1/auth/login. Blocking IP. Please review code for vulnerabilities."
    },
    {
        "sender": "HR Director <hr@tarento.com>",
        "subject": "Resource Crunch - Need 2 more Java devs",
        "content": "The E-Gov project is falling behind schedule. The current team is fully loaded. We need to allocate 2 senior Java Spring Boot developers immediately to meet the Q1 deadline."
    },
    {
        "sender": "Support Team <support@tarento.com>",
        "subject": "Legacy System Maintenance - Downtime Required",
        "content": "We need to schedule a 2-hour downtime window this Sunday for patching the legacy Oracle database. Please communicate this to all affected stakeholders."
    },
    {
        "sender": "Client Feedback <feedback@client.com>",
        "subject": "UI/UX Review - Dashboard colors",
        "content": "The new dark mode contrast is too low. It is hard to read the charts on the projector during meetings. Can we increase the brightness of the primary text color?"
    },
    {
        "sender": "Automated Test <ci@tarento.com>",
        "subject": "Build Failed: Integration Tests",
        "content": "The nightly build failed. 14 integration tests failed in the 'PaymentModule'. Please investigate recent commits by the backend team."
    },
    {
        "sender": "Legal <legal@client.com>",
        "subject": "GDPR Compliance Question",
        "content": "Are we sure we are scrubbing PII from the logs? I found a log entry that seems to contain a user's full phone number. This is a potential compliance violation."
    }
]

async def generate_live_traffic():
    print("🚀 Generating LIVE Traffic (Triggering AI Agents)...")
    async with AsyncSessionLocal() as db:
        for i, item in enumerate(SCENARIOS):
            print(f"[{i+1}/{len(SCENARIOS)}] Processing: {item['subject']}")
            try:
                result = await email_service.process_simulated_email(
                    subject=item['subject'],
                    content=item['content'],
                    sender=item['sender'],
                    db_session=db
                )
                print(f"   ✅ Processed! ID: {result.get('complaint_id')} | Category: {result.get('category')} | Severity: {result.get('severity')}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
            
            # Small delay to make it feel natural if watching logs, but fast enough for the user
            await asyncio.sleep(0.5)

    print("\n✅ Generation Complete. Check the Dashboard for new live complaints.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(generate_live_traffic())
