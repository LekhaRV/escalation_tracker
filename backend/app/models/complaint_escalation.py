"""
Tarento AI Complaint Tracking System - Complaint Escalation Model
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import uuid

from app.database import Base, TimestampMixin


class ComplaintEscalation(Base, TimestampMixin):
    """Complaint Escalation model - tracks escalation history"""
    
    __tablename__ = "complaint_escalations"
    
    escalation_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    complaint_id = Column(
        UUID(as_uuid=True),
        ForeignKey("complaints.complaint_id", ondelete="CASCADE"),
        nullable=False
    )
    escalation_level = Column(Integer, nullable=False)  # 1, 2, or 3
    escalated_to_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL")
    )
    escalation_reason = Column(Text)  # Reason for escalation
    escalated_by = Column(String(50), default="agent")  # "agent", "admin", "manager"
    escalated_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    complaint = relationship("Complaint", back_populates="escalations")
    escalated_user = relationship(
        "User",
        back_populates="escalations",
        foreign_keys=[escalated_to_user_id]
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_ce_complaint_id", "complaint_id"),
        Index("ix_ce_escalated_at", "escalated_at"),
    )
    
    def __repr__(self):
        return f"<ComplaintEscalation(escalation_id={self.escalation_id}, level={self.escalation_level})>"
