"""
Tarento AI Complaint Tracking System - Organization Model
"""

from sqlalchemy import Column, String, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import OrgStatus

class Organization(Base, TimestampMixin):
    """Organization/Tenant model"""
    
    __tablename__ = "organizations"
    
    org_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    org_name = Column(String(255), nullable=False)
    status = Column(
        SQLEnum(OrgStatus, name="org_status"),
        default=OrgStatus.ACTIVE,
        nullable=False
    )
    email_config = Column(JSON)  # Domain, IMAP settings
    settings = Column(JSON)      # SLA, Routing rules
    
    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    complaints = relationship("Complaint", back_populates="organization")
    departments = relationship("Department", back_populates="organization")
    insights = relationship("ComplaintInsight", back_populates="organization")
    patterns = relationship("ComplaintPattern", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(org_id={self.org_id}, name={self.org_name})>"
