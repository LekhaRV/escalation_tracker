"""
Tarento AI Complaint Tracking System - Gemini AI Service
Google Gemini API integration for categorization and insights
"""

import json
from typing import Optional, Dict, Any, List
import google.generativeai as genai

from app.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import logger


class GeminiService:
    """Service for Google Gemini AI integration"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        self._model = None
    
    def _get_model(self):
        """Get or create Gemini model instance"""
        if not self._model and self.api_key:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
        return self._model
    
    async def categorize_complaint(
        self,
        subject: str,
        description: str,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use Gemini to categorize a complaint
        
        Returns dict with:
        - category_type
        - sub_category
        - severity
        - priority
        - department
        - confidence_score
        - reasoning
        """
        model = self._get_model()
        
        if not model:
            logger.warning("Gemini API not configured, using fallback categorization")
            return self._fallback_categorization(subject, description)
        
        prompt = f"""Analyze this complaint for Tarento Technologies, a technology consulting company.

Subject: {subject}
Description: {description or 'No description provided'}
Project: {project_name or 'Unknown'} ({client_name or 'Unknown client'})

Categorize this complaint and return a JSON object with exactly these fields:
{{
    "category_type": "project_delivery|technical|communication|resource|billing|quality|support|engagement",
    "sub_category": "specific sub-category from the list below",
    "severity": "low|medium|high|critical",
    "priority": 1-5 (1 being highest priority),
    "department": "suggested department to handle this",
    "confidence_score": 0.0-1.0,
    "reasoning": "brief explanation of categorization"
}}

Sub-categories by category:
- project_delivery: milestone_delays, scope_creep, quality_issues, incomplete_features, documentation_gaps
- technical: architecture_decisions, performance_issues, integration_problems, security_vulnerabilities, scalability_issues
- communication: delayed_updates, unclear_requirements, unresponsive_pm, miscommunication
- resource: team_unavailability, skill_mismatch, resource_changes, insufficient_team_size
- billing: invoice_discrepancies, billing_cycle_issues, change_order_disputes, rate_disagreements
- quality: code_review_failures, non_compliance_standards, accessibility_issues
- support: slow_bug_resolution, production_issues, sla_breaches, inadequate_coverage
- engagement: expectation_mismatch, lack_of_recommendations, stakeholder_management_issues

Consider business impact when determining severity:
- critical: Production down, security breach, major financial impact
- high: Significant delays, client escalation, major functionality issues
- medium: Notable issues affecting timeline or quality
- low: Minor issues, suggestions, general feedback

Return ONLY the JSON object, no additional text."""

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            
            # Parse response
            response_text = response.text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["category_type", "severity", "priority"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini categorization failed: {str(e)}")
            return self._fallback_categorization(subject, description)
    
    def _fallback_categorization(
        self,
        subject: str,
        description: str
    ) -> Dict[str, Any]:
        """Fallback categorization when Gemini is unavailable"""
        # Simple keyword-based categorization
        text = f"{subject} {description}".lower()
        
        category_keywords = {
            "technical": ["bug", "error", "crash", "performance", "api", "code", "server"],
            "billing": ["invoice", "payment", "billing", "charge", "cost", "price"],
            "communication": ["update", "response", "contact", "message", "call"],
            "project_delivery": ["delay", "deadline", "milestone", "delivery", "late"],
            "quality": ["quality", "review", "standard", "test"],
            "support": ["help", "support", "issue", "problem"],
            "resource": ["team", "resource", "staff", "availability"],
            "engagement": ["expectation", "meeting", "stakeholder"]
        }
        
        # Find best matching category
        best_category = "support"
        best_score = 0
        
        for category, keywords in category_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > best_score:
                best_score = score
                best_category = category
        
        # Determine severity based on keywords
        severity = "medium"
        if any(w in text for w in ["urgent", "critical", "emergency", "down", "broken"]):
            severity = "critical"
        elif any(w in text for w in ["important", "serious", "major"]):
            severity = "high"
        elif any(w in text for w in ["minor", "small", "suggestion"]):
            severity = "low"
        
        return {
            "category_type": best_category,
            "sub_category": "general",
            "severity": severity,
            "priority": {"critical": 1, "high": 2, "medium": 3, "low": 4}.get(severity, 3),
            "department": self._get_department(best_category),
            "confidence_score": 0.5,
            "reasoning": "Categorized using keyword matching (Gemini unavailable)"
        }
    
    def _get_department(self, category: str) -> str:
        """Map category to department"""
        mapping = {
            "project_delivery": "Project Management",
            "technical": "Engineering",
            "communication": "Account Management",
            "resource": "Resource Management",
            "billing": "Finance",
            "quality": "Quality Assurance",
            "support": "Support",
            "engagement": "Account Management"
        }
        return mapping.get(category, "Support")
    
    async def detect_patterns(
        self,
        complaints_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Use Gemini to detect patterns in complaints"""
        model = self._get_model()
        
        if not model or len(complaints_data) < 5:
            return []
        
        # Prepare summary of complaints
        summaries = []
        for c in complaints_data[:50]:  # Limit to 50 complaints
            summaries.append(f"- {c.get('category', 'unknown')}: {c.get('subject', '')[:100]}")
        
        prompt = f"""Analyze these complaints from the last 30 days and identify patterns:

{chr(10).join(summaries)}

Identify patterns and return a JSON array:
[
    {{
        "pattern_type": "recurring|trending|systemic",
        "description": "description of the pattern",
        "frequency": number of occurrences,
        "severity_score": 0.0-1.0,
        "affected_categories": ["list of categories"],
        "recommendation": "what action to take"
    }}
]

Pattern types:
- recurring: Same problem happening repeatedly
- trending: Issue frequency is increasing
- systemic: Root cause affecting multiple areas

Return ONLY the JSON array."""

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048
                )
            )
            
            response_text = response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            patterns = json.loads(response_text)
            return patterns if isinstance(patterns, list) else []
            
        except Exception as e:
            logger.error(f"Gemini pattern detection failed: {str(e)}")
            return []
    
    async def generate_insights(
        self,
        analytics_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use Gemini to generate executive insights"""
        model = self._get_model()
        
        if not model:
            return {"insights": [], "executive_summary": "Gemini API not configured"}
        
        prompt = f"""Based on these analytics from Tarento Technologies complaint system:

Total complaints: {analytics_data.get('total_complaints', 0)}
By category: {analytics_data.get('by_category', {})}
By project: {analytics_data.get('by_project', {})}
Resolution time avg: {analytics_data.get('avg_resolution_hours', 0)} hours
SLA compliance: {analytics_data.get('sla_compliance', 0)}%

Generate insights and return JSON:
{{
    "insights": [
        {{
            "insight_type": "trend|recommendation|alert",
            "title": "short title",
            "description": "detailed description",
            "impact_level": "low|medium|high",
            "actionable": true/false,
            "recommendations": ["list of action items"]
        }}
    ],
    "executive_summary": "2-3 sentence summary for executives"
}}

Return ONLY the JSON object."""

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=2048
                )
            )
            
            response_text = response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"Gemini insight generation failed: {str(e)}")
            return {
                "insights": [],
                "executive_summary": "Could not generate insights"
            }


# Singleton instance
gemini_service = GeminiService()
