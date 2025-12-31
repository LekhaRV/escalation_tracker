
import asyncio
import sys
import os
from sqlalchemy import select

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.gemini_service import gemini_service
from app.services.analytics_service import AnalyticsService
from app.models import Organization, ComplaintInsight
from app.utils.constants import InsightType

async def generate_insights():
    print("🧠 Generating insights...")
    async with AsyncSessionLocal() as db:
        # Get org
        result = await db.execute(select(Organization).limit(1))
        org = result.scalars().first()
        if not org:
            print("No org found")
            return

        # Get analytics data
        analytics = AnalyticsService(db)
        stats = await analytics.get_dashboard_stats(org.org_id)
        
        # Prepare data for Gemini
        analytics_summary = {
            "total_complaints": stats["total_complaints"],
            "by_category": {
                "critical": stats["critical_count"],
                "high": stats["high_count"],
                "medium": stats["medium_count"] 
            },
            "sla_compliance": stats["sla_compliance_rate"]
        }
        
        # Call Gemini with fallback
        try:
            result = await gemini_service.generate_insights(analytics_summary)
        except Exception as e:
            print(f"Gemini failed: {e}")
            result = {}
            
        print(f"Generated {len(result.get('insights', []))} insights")
        
        # Save insights
        new_insights = []
        
        # Use AI insights if available
        for item in result.get("insights", [])[:3]: 
            insight = ComplaintInsight(
                org_id=org.org_id,
                title=item.get("title", "Insight"),
                description=item.get("description", "No description"),
                insight_type=InsightType.RECOMMENDATION,
                impact_level=item.get("impact_level", "medium").lower(),
                actionable=True
            )
            new_insights.append(insight)
            
        # Fallback if no AI insights (e.g. rate limit)
        if not new_insights:
            print("⚠️ Using fallback rule-based insights due to API limits")
            if stats["overdue_complaints"] > 0:
                new_insights.append(ComplaintInsight(
                    org_id=org.org_id,
                    title="SLA Breaches Detected",
                    description=f"There are {stats['overdue_complaints']} overdue complaints. Immediate attention required.",
                    insight_type=InsightType.ALERT,
                    impact_level="high",
                    actionable=True
                ))
            
            if stats["critical_count"] > 0:
                 new_insights.append(ComplaintInsight(
                    org_id=org.org_id,
                    title="Critical Issues Spike",
                    description=f"High volume of critical issues ({stats['critical_count']}). Review resource allocation.",
                    insight_type=InsightType.ALERT,
                    impact_level="high",
                    actionable=True
                ))
                
            new_insights.append(ComplaintInsight(
                org_id=org.org_id,
                title="Weekly Volume",
                description=f"Total of {stats['complaints_this_week']} complaints received this week.",
                insight_type=InsightType.TREND,
                impact_level="medium",
                actionable=False
            ))

        if new_insights:
            db.add_all(new_insights)
            await db.commit()
            print("✅ Insights saved to DB")
        else:
            print("No new insights generated")

if __name__ == "__main__":
    asyncio.run(generate_insights())
