"""
Tarento AI Complaint Tracking System - Complaint Pattern Model
AI pattern detection results
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import PatternType, PatternStatus


class ComplaintPattern(Base, TimestampMixin):
    """Complaint Pattern model - AI-detected patterns"""
    
    __tablename__ = "complaint_patterns"
    
    pattern_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Pattern details
    pattern_type = Column(
        SQLEnum(PatternType, name="pattern_type"),
        nullable=False
    )
    pattern_description = Column(Text)
    affected_complaints = Column(JSON, default=list)  # Array of complaint IDs
    affected_projects = Column(JSON, default=list)  # Array of project IDs
    
    # Metrics
    frequency = Column(Integer, default=1)  # How often this pattern occurs
    severity_score = Column(Numeric(3, 2), default=0.0)  # 0.00 to 1.00
    
    # Status
    status = Column(
        SQLEnum(PatternStatus, name="pattern_status"),
        default=PatternStatus.ACTIVE
    )
    detected_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    organization = relationship("Organization", back_populates="patterns")
    
    # Indexes
    __table_args__ = (
        Index("ix_cp_org_id", "org_id"),
        Index("ix_cp_pattern_type", "pattern_type"),
        Index("ix_cp_status", "status"),
        Index("ix_cp_detected_at", "detected_at"),
    )
    
    def __repr__(self):
        return f"<ComplaintPattern(pattern_id={self.pattern_id}, type={self.pattern_type})>"
