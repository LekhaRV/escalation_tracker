"""
Tarento AI Complaint Tracking System - Complaint Category Model
AI categorization results
"""

from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import SeverityLevel


class ComplaintCategory(Base, TimestampMixin):
    """Complaint Category model - stores AI categorization results"""
    
    __tablename__ = "complaint_categories"
    
    category_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    complaint_id = Column(
        UUID(as_uuid=True),
        ForeignKey("complaints.complaint_id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    
    # Categorization
    category_type = Column(String(100), nullable=False)  # project_delivery, technical, etc.
    sub_category = Column(String(100))  # milestone_delays, performance_issues, etc.
    severity = Column(
        SQLEnum(SeverityLevel, name="severity_level"),
        nullable=False
    )
    priority = Column(Integer, default=3)  # 1-5, 1 being highest
    department = Column(String(100))  # Suggested department
    
    # AI metadata
    confidence_score = Column(Numeric(3, 2), default=0.0)  # 0.00 to 1.00
    categorized_by = Column(String(50), default="agent")  # "agent" or "manual"
    categorized_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    complaint = relationship("Complaint", back_populates="category")
    
    # Indexes
    __table_args__ = (
        Index("ix_cc_category_type", "category_type"),
        Index("ix_cc_severity", "severity"),
        Index("ix_cc_department", "department"),
    )
    
    def __repr__(self):
        return f"<ComplaintCategory(category_id={self.category_id}, type={self.category_type}, severity={self.severity})>"
