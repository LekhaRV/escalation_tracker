"""
Tarento AI Complaint Tracking System - Organization Model
Multi-tenant root entity
"""

from sqlalchemy import Column, String, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import OrgStatus


class Organization(Base, TimestampMixin):
    """Organization model - multi-tenant root"""
    
    __tablename__ = "organizations"
    
    org_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    org_name = Column(String(255), nullable=False)
    email_config = Column(JSON, default=dict)  # IMAP settings for this org
    settings = Column(JSON, default=dict)  # General org settings
    status = Column(
        SQLEnum(OrgStatus, name="org_status"),
        default=OrgStatus.ACTIVE,
        nullable=False
    )
    
    # Relationships
    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    projects = relationship(
        "Project",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    complaints = relationship(
        "Complaint",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    patterns = relationship(
        "ComplaintPattern",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    insights = relationship(
        "ComplaintInsight",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Organization(org_id={self.org_id}, org_name={self.org_name})>"
