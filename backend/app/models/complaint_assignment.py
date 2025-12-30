"""
Tarento AI Complaint Tracking System - Complaint Assignment Model
Routing results
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import uuid

from app.database import Base, TimestampMixin


class ComplaintAssignment(Base, TimestampMixin):
    """Complaint Assignment model - stores routing results"""
    
    __tablename__ = "complaint_assignments"
    
    assignment_id = Column(
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
    assigned_to_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL")
    )
    assigned_to_team = Column(String(100))  # Fallback if no specific user
    
    # Assignment metadata
    assignment_reason = Column(String(255))  # "project_member (score: 85.5)", "category_match", etc.
    sla_deadline = Column(DateTime(timezone=True), nullable=False)
    assigned_by = Column(String(50), default="agent")  # "agent", "admin", "manager"
    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    complaint = relationship("Complaint", back_populates="assignment")
    assigned_user = relationship(
        "User",
        back_populates="assignments",
        foreign_keys=[assigned_to_user_id]
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_ca_assigned_to", "assigned_to_user_id"),
        Index("ix_ca_assigned_to_team", "assigned_to_team"),
        Index("ix_ca_sla_deadline", "sla_deadline"),
    )
    
    def __repr__(self):
        return f"<ComplaintAssignment(assignment_id={self.assignment_id}, user={self.assigned_to_user_id})>"
