"""
Tarento AI Complaint Tracking System - Complaint Insight Model
AI-generated insights
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import InsightType, ImpactLevel


class ComplaintInsight(Base, TimestampMixin):
    """Complaint Insight model - AI-generated insights and recommendations"""
    
    __tablename__ = "complaint_insights"
    
    insight_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Insight details
    insight_type = Column(
        SQLEnum(InsightType, name="insight_type"),
        nullable=False
    )
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Related data
    related_patterns = Column(JSON, default=list)  # Array of pattern IDs
    related_projects = Column(JSON, default=list)  # Array of project IDs
    
    # Impact
    impact_level = Column(
        SQLEnum(ImpactLevel, name="impact_level"),
        default=ImpactLevel.MEDIUM
    )
    actionable = Column(Boolean, default=True)
    
    # Timestamps
    generated_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    organization = relationship("Organization", back_populates="insights")
    
    # Indexes
    __table_args__ = (
        Index("ix_ci_org_id", "org_id"),
        Index("ix_ci_insight_type", "insight_type"),
        Index("ix_ci_impact_level", "impact_level"),
        Index("ix_ci_generated_at", "generated_at"),
    )
    
    def __repr__(self):
        return f"<ComplaintInsight(insight_id={self.insight_id}, title={self.title[:50]})>"
