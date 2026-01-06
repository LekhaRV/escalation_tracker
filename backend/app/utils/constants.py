"""
Tarento AI Complaint Tracking System - Utility Constants
"""

from enum import Enum
from typing import Dict, List


# User Roles
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    AGENT = "AGENT"
    VIEWER = "VIEWER"


# Organization Status
class OrgStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


# User Status
class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# Project Status
class ProjectStatus(str, Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# Complaint Status
class ComplaintStatus(str, Enum):
    NEW = "NEW"
    CATEGORIZED = "CATEGORIZED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


# Severity Levels
class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Pattern Types
class PatternType(str, Enum):
    RECURRING = "RECURRING"
    TRENDING = "TRENDING"
    SYSTEMIC = "SYSTEMIC"


# Pattern Status
class PatternStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    MONITORING = "MONITORING"


# Insight Types
class InsightType(str, Enum):
    TREND = "TREND"
    RECOMMENDATION = "RECOMMENDATION"
    ALERT = "ALERT"


# Impact Levels
class ImpactLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# Agent Log Status
class AgentLogStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"


# Tarento-Specific Categories
CATEGORY_TYPES: List[str] = [
    "project_delivery",
    "technical",
    "communication",
    "resource",
    "billing",
    "quality",
    "support",
    "engagement"
]


# Sub-categories by Category
SUB_CATEGORIES: Dict[str, List[str]] = {
    "project_delivery": [
        "milestone_delays",
        "scope_creep",
        "quality_issues",
        "incomplete_features",
        "documentation_gaps"
    ],
    "technical": [
        "architecture_decisions",
        "performance_issues",
        "integration_problems",
        "security_vulnerabilities",
        "scalability_issues"
    ],
    "communication": [
        "delayed_updates",
        "unclear_requirements",
        "unresponsive_pm",
        "miscommunication"
    ],
    "resource": [
        "team_unavailability",
        "skill_mismatch",
        "resource_changes",
        "insufficient_team_size"
    ],
    "billing": [
        "invoice_discrepancies",
        "billing_cycle_issues",
        "change_order_disputes",
        "rate_disagreements"
    ],
    "quality": [
        "code_review_failures",
        "non_compliance_standards",
        "accessibility_issues"
    ],
    "support": [
        "slow_bug_resolution",
        "production_issues",
        "sla_breaches",
        "inadequate_coverage"
    ],
    "engagement": [
        "expectation_mismatch",
        "lack_of_recommendations",
        "stakeholder_management_issues"
    ]
}


# Category to Department Mapping
# Maps AI-detected category types to Tarento departments
CATEGORY_DEPARTMENT_MAP: Dict[str, str] = {
    # Primary categories
    "project_delivery": "Delivery",
    "technical": "Engineering",
    "communication": "Client Success",
    "resource": "HR",
    "billing": "Finance",
    "quality": "Quality Assurance",
    "support": "Client Success",
    "engagement": "Client Success",
    # Technical sub-categories
    "infrastructure": "DevOps",
    "api": "Engineering",
    "bug": "Engineering",
    "performance": "Engineering",
    "security": "DevOps",
    "deployment": "DevOps",
    "cloud": "DevOps",
    # Delivery sub-categories
    "delay": "Delivery",
    "timeline": "Delivery",
    "milestone": "Delivery",
    "scope": "Delivery",
    # Finance sub-categories
    "invoice": "Finance",
    "payment": "Finance",
    # Quality sub-categories
    "testing": "Quality Assurance",
    "qa": "Quality Assurance",
    # Design categories
    "design": "Design",
    "ux": "Design",
    "ui": "Design",
    # Data categories
    "data": "Data & AI",
    "analytics": "Data & AI",
    "ml": "Data & AI",
    "ai": "Data & AI",
}


# Project Team Roles
PROJECT_ROLES: List[str] = [
    "project_manager",
    "team_lead",
    "backend_lead",
    "frontend_lead",
    "backend_developer",
    "frontend_developer",
    "fullstack_developer",
    "qa_engineer",
    "qa_lead",
    "devops_engineer",
    "ui_ux_designer",
    "business_analyst",
    "technical_architect"
]


# Role Score Points for Assignment
ROLE_SCORE_POINTS: Dict[str, int] = {
    "project_manager": 40,
    "team_lead": 40,
    "backend_lead": 35,
    "frontend_lead": 35,
    "technical_architect": 35,
    "qa_lead": 30,
    "backend_developer": 25,
    "frontend_developer": 25,
    "fullstack_developer": 25,
    "qa_engineer": 25,
    "devops_engineer": 25,
    "ui_ux_designer": 20,
    "business_analyst": 20
}


# Severity Multipliers
SEVERITY_MULTIPLIERS: Dict[str, float] = {
    "critical": 1.3,
    "high": 1.2,
    "medium": 1.0,
    "low": 0.9
}


# Specializations
SPECIALIZATIONS: List[str] = [
    "api_design",
    "performance",
    "security",
    "database",
    "frontend",
    "backend",
    "devops",
    "testing",
    "architecture",
    "ui_ux",
    "mobile",
    "cloud",
    "microservices",
    "integration"
]
