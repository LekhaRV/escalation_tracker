"""
Tarento AI Complaint Tracking System - Project Team Member Model
CRITICAL for project-based routing
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base, TimestampMixin


class ProjectTeamMember(Base, TimestampMixin):
    """
    Project Team Member model - Maps users to projects with roles and specializations
    CRITICAL for project-based intelligent routing
    """
    
    __tablename__ = "project_team_members"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    role = Column(String(100), nullable=False)  # backend_lead, frontend_developer, etc.
    specialization = Column(JSON, default=list)  # ["api_design", "performance", "security"]
    is_active = Column(Boolean, default=True)
    workload_capacity = Column(Integer, default=10)  # Max concurrent complaints
    current_workload = Column(Integer, default=0)  # Current active complaints
    priority_order = Column(Integer, default=1)  # For assignment priority
    joined_at = Column(
        String(50),
        default=lambda: datetime.utcnow().isoformat()
    )
    
    # Relationships
    project = relationship("Project", back_populates="team_members")
    user = relationship("User", back_populates="project_memberships")
    
    # Indexes
    __table_args__ = (
        Index("ix_ptm_project_id", "project_id"),
        Index("ix_ptm_user_id", "user_id"),
        Index("ix_ptm_is_active", "is_active"),
    )
    
    def __repr__(self):
        return f"<ProjectTeamMember(project_id={self.project_id}, user_id={self.user_id}, role={self.role})>"
