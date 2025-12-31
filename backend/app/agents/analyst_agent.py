"""
Tarento AI Complaint Tracking System - Analyst Agent
Interprets natural language queries about data and returns insights
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime

from app.services.gemini_service import gemini_service
from app.services.analytics_service import AnalyticsService
from app.core.logging import logger

class AnalystAgent:
    """
    AI Analyst Agent
    Interprets user questions about data and fetches relevant analytics.
    """
    
    def __init__(self, db: AsyncSession, org_id: Any):
        self.db = db
        self.org_id = org_id
        self.analytics = AnalyticsService(db)
        
    async def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return answer + data
        """
        # 1. Intent Classification
        intent = await self._classify_intent(query)
        logger.info(f"Analyst Agent Intent: {intent}")
        
        # 2. Fetch Data
        data = {}
        if intent == "dashboard_stats":
            data = await self.analytics.get_dashboard_stats(self.org_id)
        elif intent == "trends":
            data = {"trends": await self.analytics.get_daily_trends(self.org_id, days=30)}
        elif intent == "patterns":
            data = {"patterns": await self.analytics.get_patterns(self.org_id)}
        elif intent == "insights":
            data = {"insights": await self.analytics.get_insights(self.org_id)}
        else:
            # Default to dashboard stats for general questions
            data = await self.analytics.get_dashboard_stats(self.org_id)
            
        # 3. Generate Natural Language Answer
        answer = await self._generate_answer(query, data, intent)
        
        return {
            "query": query,
            "intent": intent,
            "answer": answer,
            "data": data, # Return raw data for frontend charts if needed
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _classify_intent(self, query: str) -> str:
        """Classify query into data needs"""
        prompt = f"""Classify this analytics query into one of these intents:
        - dashboard_stats (general counts, overview, specific numbers like 'how many')
        - trends (time-based data, history, 'last week', 'trend')
        - patterns (recurring issues, common problems)
        - insights (AI analysis, recommendations, deeper meaning)
        
        Query: "{query}"
        
        Return ONLY the intent name string."""
        
        response = await gemini_service._generate_content(prompt, temperature=0.1)
        return response.strip().lower() if response else "dashboard_stats"

    async def _generate_answer(self, query: str, data: Dict[str, Any], intent: str) -> str:
        """Generate human-friendly answer based on data"""
        # Simplify data for context window if too large
        data_str = json.dumps(data, default=str)[:4000] 
        
        prompt = f"""You are an AI Data Analyst for the Tarento Complaint System.
        User Query: "{query}"
        
        Data Retrieved ({intent}):
        {data_str}
        
        Answer the user's question clearly and concisely based on this data. 
        - If the user asks for a specific number, give it.
        - If the user asks for a summary, provide high-level key points.
        - Use professional, helpful tone.
        - If data is empty, say so politely.
        """
        
        response = await gemini_service._generate_content(prompt, temperature=0.3)
        return response or "I couldn't generate an answer from the data."
