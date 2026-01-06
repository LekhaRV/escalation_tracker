"""
Tarento AI Complaint Tracking System - Complaint Model
Core entity for complaint tracking
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import ComplaintStatus


class Complaint(Base, TimestampMixin):
    """Complaint model - core entity"""
    
    __tablename__ = "complaints"
    
    complaint_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.project_id", ondelete="SET NULL"),
        nullable=True  # Can be unlinked initially, critical for routing
    )
    
    # Email tracking
    email_id = Column(String(255))  # Unique email ID from IMAP
    
    # Customer info
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    
    # Complaint content
    subject = Column(String(500), nullable=False)
    description = Column(Text)
    ai_summary = Column(Text, nullable=True)  # AI-generated executive summary
    raw_email_content = Column(Text)  # Original email content
    
    # Status
    status = Column(
        SQLEnum(ComplaintStatus, name="complaint_status"),
        default=ComplaintStatus.NEW,
        nullable=False
    )
    
    # Resolution
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    organization = relationship("Organization", back_populates="complaints")
    project = relationship("Project", back_populates="complaints")
    category = relationship(
        "ComplaintCategory",
        back_populates="complaint",
        uselist=False,
        cascade="all, delete-orphan"
    )
    assignment = relationship(
        "ComplaintAssignment",
        back_populates="complaint",
        uselist=False,
        cascade="all, delete-orphan"
    )
    escalations = relationship(
        "ComplaintEscalation",
        back_populates="complaint",
        cascade="all, delete-orphan"
    )
    agent_logs = relationship(
        "AgentLog",
        back_populates="complaint",
        cascade="all, delete-orphan"
    )
    comments = relationship(
        "ComplaintComment",
        back_populates="complaint",
        cascade="all, delete-orphan",
        order_by="ComplaintComment.created_at.desc()"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_complaints_org_id", "org_id"),
        Index("ix_complaints_project_id", "project_id"),
        Index("ix_complaints_status", "status"),
        Index("ix_complaints_customer_email", "customer_email"),
        Index("ix_complaints_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<Complaint(complaint_id={self.complaint_id}, subject={self.subject[:50]})>"
