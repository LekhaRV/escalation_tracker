"""
Tarento AI Complaint Tracking System - Project Model
Tarento-specific project with team management
"""

from sqlalchemy import Column, String, Text, Date, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import ProjectStatus


class Project(Base, TimestampMixin):
    """Project model - Tarento-specific with team management"""
    
    __tablename__ = "projects"
    
    project_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False
    )
    department_id = Column(
        UUID(as_uuid=True),
        ForeignKey("departments.department_id", ondelete="SET NULL"),
        nullable=True  # Optional - projects are cross-functional
    )
    project_name = Column(String(255), nullable=False)
    project_code = Column(String(50))  # Short code like "ABC-API"
    client_name = Column(String(255))
    description = Column(Text)
    project_manager_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL")
    )
    team_lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL")
    )
    status = Column(
        SQLEnum(ProjectStatus, name="project_status"),
        default=ProjectStatus.PLANNING,
        nullable=False
    )
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    department = relationship("Department", back_populates="projects")
    project_manager = relationship(
        "User",
        back_populates="managed_projects",
        foreign_keys=[project_manager_id]
    )

    @property
    def department_name(self):
        return self.department.name if self.department else None
    team_lead = relationship(
        "User",
        back_populates="led_projects",
        foreign_keys=[team_lead_id]
    )
    team_members = relationship(
        "ProjectTeamMember",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    complaints = relationship(
        "Complaint",
        back_populates="project"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_projects_org_id", "org_id"),
        Index("ix_projects_status", "status"),
        Index("ix_projects_client_name", "client_name"),
    )
    
    def __repr__(self):
        return f"<Project(project_id={self.project_id}, project_name={self.project_name})>"
