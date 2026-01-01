"""
Tarento AI Complaint Tracking System - Utility Helpers
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
import math

from app.config import settings
from app.utils.constants import SeverityLevel


def calculate_sla_deadline(
    severity: str,
    created_at: Optional[datetime] = None
) -> datetime:
    """Calculate SLA deadline based on severity level"""
    if created_at is None:
        created_at = datetime.utcnow()
    
    # SLA Policy: 2 Months (60 Days) for all complaints
    # Warnings at 7 days remaining
    sla_hours = {
        SeverityLevel.CRITICAL.value: 24 * 60, # 1440 hours
        SeverityLevel.HIGH.value: 24 * 60,
        SeverityLevel.MEDIUM.value: 24 * 60,
        SeverityLevel.LOW.value: 24 * 60
    }
    
    hours = sla_hours.get(severity, 24 * 60)
    return created_at + timedelta(hours=hours)


def paginate(
    items: List[Any],
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """Paginate a list of items"""
    total = len(items)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Ensure valid page number
    page = max(1, min(page, total_pages))
    
    # Calculate slice indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        "items": items[start_idx:end_idx],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO format string"""
    if dt is None:
        return None
    return dt.isoformat()


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO format string to datetime"""
    if dt_str is None:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def uuid_to_str(uuid_val: Optional[UUID]) -> Optional[str]:
    """Convert UUID to string"""
    if uuid_val is None:
        return None
    return str(uuid_val)


def calculate_assignment_score(
    role: str,
    specialization: List[str],
    workload: int,
    workload_capacity: int,
    severity: str,
    category_keywords: List[str]
) -> float:
    """
    Calculate assignment score for project-based routing
    
    Score components:
    - Role match: 0-40 points
    - Specialization match: 0-40 points
    - Workload availability: 0-20 points
    
    Final score multiplied by severity factor
    """
    from app.utils.constants import ROLE_SCORE_POINTS, SEVERITY_MULTIPLIERS
    
    # Role score (0-40)
    role_score = ROLE_SCORE_POINTS.get(role, 15)
    
    # Specialization score (0-40)
    spec_matches = sum(
        1 for keyword in category_keywords
        if any(keyword.lower() in spec.lower() for spec in specialization)
    )
    spec_score = min(40, spec_matches * 10)
    
    # Workload score (0-20) - less workload = higher score
    if workload_capacity > 0:
        workload_ratio = workload / workload_capacity
        workload_score = max(0, 20 * (1 - workload_ratio))
    else:
        workload_score = 0
    
    # Base score
    base_score = role_score + spec_score + workload_score
    
    # Apply severity multiplier
    multiplier = SEVERITY_MULTIPLIERS.get(severity, 1.0)
    final_score = base_score * multiplier
    
    return round(final_score, 2)


def get_category_keywords(category_type: str, sub_category: str) -> List[str]:
    """Extract keywords from category for specialization matching"""
    keywords = []
    
    # Add category-based keywords
    category_keyword_map = {
        "technical": ["backend", "api", "architecture", "performance", "integration"],
        "project_delivery": ["project", "delivery", "management"],
        "quality": ["testing", "qa", "quality"],
        "support": ["support", "bug", "production"],
        "billing": ["billing", "finance"],
        "communication": ["communication", "account"],
        "resource": ["resource", "team"],
        "engagement": ["account", "stakeholder"]
    }
    
    keywords.extend(category_keyword_map.get(category_type, []))
    
    # Add sub-category based keywords
    sub_category_map = {
        "performance_issues": ["performance", "optimization"],
        "security_vulnerabilities": ["security"],
        "integration_problems": ["integration", "api"],
        "architecture_decisions": ["architecture"],
        "scalability_issues": ["scalability", "cloud"],
        "production_issues": ["devops", "production"],
        "code_review_failures": ["backend", "frontend", "testing"]
    }
    
    keywords.extend(sub_category_map.get(sub_category, []))
    
    return list(set(keywords))


def mask_email(email: str) -> str:
    """Mask email for privacy in logs"""
    if "@" not in email:
        return email
    
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
