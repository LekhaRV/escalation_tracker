"""
Tarento AI Complaint Tracking System - Gemini AI Service
Google Gemini API integration for categorization and insights (using HTTPX)
"""

import json
from typing import Optional, Dict, Any, List
import httpx

from app.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import logger


class GeminiService:
    """Service for Google Gemini AI integration via REST API"""
    
    def __init__(self):
        # Prefer GROQ_API_KEY from settings
        self.api_key = settings.GROQ_API_KEY or settings.GEMINI_API_KEY
        
        # Log key prefix for debugging
        if self.api_key:
            logger.info(f"Initialized AI Service with Key: {self.api_key[:5]}... Model: {settings.GEMINI_MODEL}")
            
        # Use Groq's Llama 3.3 70B (Latest Stable)
        self.model_name = "llama-3.3-70b-versatile"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def _generate_content(self, prompt: str, temperature: float = 0.2) -> Optional[str]:
        """Generate content using Groq (OpenAI Compatible) API"""
        if not self.api_key:
            return None
            
        import asyncio
        max_retries = 3
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    payload = {
                        "model": self.model_name,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": 2048
                    }
                    
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data["choices"][0]["message"]["content"]
                        
                    elif response.status_code == 429:
                        logger.warning(f"Groq Rate Limit. Retrying... (Attempt {attempt+1})")
                        await asyncio.sleep(2)
                        continue
                    else:
                        logger.error(f"Groq API error {response.status_code}: {response.text}")
                        return None
                        
            except Exception as e:
                logger.error(f"Groq API call failed: {str(e)}")
                if attempt < max_retries:
                     await asyncio.sleep(1)
                     continue
                return None
        
        return None
    
    async def categorize_complaint(
        self,
        subject: str,
        description: str,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use Gemini to categorize a complaint
        """
        prompt = f"""Analyze this complaint for Tarento Technologies.
        
Subject: {subject}
Description: {description or 'No description provided'}
Project: {project_name or 'Unknown'} ({client_name or 'Unknown client'})

Categorize this complaint and return a JSON object with exactly these fields:
{{
    "is_complaint": true/false (false for general inquiries, holidays, pure feedback, or spam),
    "category_type": "project_delivery|technical|communication|resource|billing|quality|support|engagement",
    "sub_category": "specific sub-category from the list below",
    "severity": "medium",
    "priority": 3,
    "department": "suggested department to handle this",
    "confidence_score": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Sub-categories by category:
- project_delivery: milestone_delays, scope_creep, quality_issues, incomplete_features
- technical: architecture_decisions, performance_issues, integration_problems, security_vulnerabilities
- communication: delayed_updates, unclear_requirements, unresponsive_pm
- resource: team_unavailability, skill_mismatch, resource_changes
- billing: invoice_discrepancies, billing_cycle_issues
- quality: code_review_failures, non_compliance_standards
- support: slow_bug_resolution, production_issues, sla_breaches
- engagement: expectation_mismatch, stakeholder_management_issues

IMPORTANT:
1. If the email is clearly NOT a complaint (e.g. asking for holiday calendar, general greeting, sales pitch), set "is_complaint": false.
2. If it is a complaint, ALWAYS set severity="medium" and priority=3. We treat all complaints equally.
3. Return ONLY the JSON object, start with {{ and end with }}."""

        response_text = await self._generate_content(prompt, temperature=0.2)
        
        if not response_text:
            logger.warning("Gemini API unavailable, using fallback")
            return self._fallback_categorization(subject, description)
            
        try:
            # Clean response to ensure valid JSON
            cleaned_text = self._clean_json(response_text)
            result = json.loads(cleaned_text)
            return result
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {str(e)}")
            return self._fallback_categorization(subject, description)

    def _clean_json(self, text: str) -> str:
        """Extract JSON from markdown code blocks if present"""
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()

    def _fallback_categorization(
        self,
        subject: str,
        description: str
    ) -> Dict[str, Any]:
        """Fallback categorization when Gemini is unavailable"""
        # Simple keyword-based categorization
        text = f"{subject} {description}".lower()
        
        # Heuristic for non-complaints (when API is down)
        # Heuristic for non-complaints (when API is down)
        non_complaint_keywords = ["holiday", "calendar", "question", "inquiry", "greeting", "thanks", "checking", "demo", "test", "ignore"]
        is_complaint = True
        
        # If it looks like a simple inquiry, mark distinct from complaint
        if any(k in text for k in non_complaint_keywords) and not any(k in text for k in ["fail", "error", "broken", "down", "bug"]):
             is_complaint = False
        
        category_keywords = {
            "technical": ["bug", "error", "crash", "performance", "api", "code"],
            "billing": ["invoice", "payment", "cost", "price"],
            "project_delivery": ["delay", "deadline", "delivery", "late"],
            "support": ["help", "issue", "problem"]
        }
        
        best_category = "support"
        if is_complaint:
            for category, keywords in category_keywords.items():
                if any(k in text for k in keywords):
                    best_category = category
                    break
        else:
            best_category = "ignored"
        
        return {
            "is_complaint": is_complaint,
            "category_type": best_category,
            "sub_category": "general",
            "severity": "medium",
            "priority": 3,
            "department": "Support",
            "confidence_score": 0.5,
            "reasoning": "Fallback keyword matching"
        }
    
    async def detect_patterns(
        self,
        complaints_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Use Gemini to detect patterns in complaints"""
        if len(complaints_data) < 3:
            return []
            
        # Summary for prompt
        summaries = [f"- {c.get('category')}: {c.get('subject')}" for c in complaints_data[:30]]
        
        prompt = f"""Analyze these complaints for recurring patterns:
{chr(10).join(summaries)}

Identify patterns and return a JSON array:
[
    {{
        "pattern_type": "recurring|trending|systemic",
        "description": "description",
        "frequency": number,
        "severity_score": 0.1-1.0,
        "affected_categories": ["cat1"],
        "recommendation": "action"
    }}
]
Return ONLY JSON array."""

        response_text = await self._generate_content(prompt, temperature=0.3)
        if not response_text:
            return []
            
        try:
            return json.loads(self._clean_json(response_text))
        except:
            return []
    
    async def generate_insights(
        self,
        analytics_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use Gemini to generate executive insights"""
        prompt = f"""Based on analytics:
Total: {analytics_data.get('total_complaints')}
Categories: {analytics_data.get('by_category')}
SLA Compliance: {analytics_data.get('sla_compliance')}%

Generate insights JSON:
{{
    "insights": [
        {{
            "insight_type": "trend|recommendation|alert",
            "title": "title",
            "description": "desc",
            "impact_level": "low|medium|high",
            "actionable": true,
            "recommendations": ["action"]
        }}
    ],
    "executive_summary": "summary text"
}}"""

        response_text = await self._generate_content(prompt, temperature=0.4)
        if not response_text:
            return {"insights": [], "executive_summary": "AI unavailable"}
            
        try:
            return json.loads(self._clean_json(response_text))
        except:
            return {"insights": [], "executive_summary": "Parsing error"}

    async def generate_resolution_recommendations(
        self,
        subject: str,
        description: str,
        category: str,
        severity: str
    ) -> List[str]:
        """Generate resolution steps for a complaint"""
        prompt = f"""Complaint Resolution Expert System.
        
Subject: {subject}
Description: {description}
Category: {category} (Severity: {severity})

Provide a checklist of 3-5 concrete, actionable steps a support agent should take to resolve this issue.
Return ONLY a JSON array of strings, e.g., ["Check logs", "Restart service"].
Do not include numbering or markdown formatting outside the array."""

        response_text = await self._generate_content(prompt, temperature=0.3)
        if not response_text:
            return ["Review internal knowledge base", "Check standard operating procedures", "Escalate if blocking"]
            
        try:
            result = json.loads(self._clean_json(response_text))
            if isinstance(result, list):
                return result
            # Handle if AI returns object with steps key
            if isinstance(result, dict) and "steps" in result:
                return result["steps"]
            return ["Review provided details", "Contact customer for more info"]
        except:
            return ["Review internal knowledge base"]

    async def summarize_complaint(self, subject: str, description: str) -> Optional[str]:
        """
        Generate a concise 1-2 line executive summary of the complaint.
        """
        prompt = f"""Summarize this complaint in 1-2 concise sentences for an executive dashboard. Focus on the core issue and impact. Do not include introductory phrases like "Here is a summary".

Subject: {subject}
Description: {description}"""

        return await self._generate_content(prompt, temperature=0.3)

gemini_service = GeminiService()
