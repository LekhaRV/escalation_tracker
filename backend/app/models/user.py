"""
Tarento AI Complaint Tracking System - User Model
"""

from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import UserRole, UserStatus


class User(Base, TimestampMixin):
    """User model with role-based access"""
    
    __tablename__ = "users"
    
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False
    )
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # bcrypt hashed
    name = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(UserRole, name="user_role"),
        default=UserRole.AGENT,
        nullable=False
    )
    team = Column(String(100))  # Team name
    department_id = Column(
        UUID(as_uuid=True),
        ForeignKey("departments.department_id", ondelete="SET NULL"),
        nullable=True
    )
    status = Column(
        SQLEnum(UserStatus, name="user_status"),
        default=UserStatus.ACTIVE,
        nullable=False
    )
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    assignments = relationship(
        "ComplaintAssignment",
        back_populates="assigned_user",
        foreign_keys="ComplaintAssignment.assigned_to_user_id"
    )
    escalations = relationship(
        "ComplaintEscalation",
        back_populates="escalated_user",
        foreign_keys="ComplaintEscalation.escalated_to_user_id"
    )
    # Department managed by this user
    managed_department = relationship(
        "Department",
        back_populates="manager",
        uselist=False,
        foreign_keys="Department.manager_id"
    )
    # Department the user belongs to
    department_link = relationship(
        "Department",
        back_populates="users",
        foreign_keys=[department_id]
    )
    # Projects where user is project manager
    managed_projects = relationship(
        "Project",
        back_populates="project_manager",
        foreign_keys="Project.project_manager_id"
    )
    # Projects where user is team lead
    led_projects = relationship(
        "Project",
        back_populates="team_lead",
        foreign_keys="Project.team_lead_id"
    )
    # Project team memberships
    project_memberships = relationship(
        "ProjectTeamMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @property
    def department_name(self):
        return self.department_link.name if self.department_link else None
    
    # Indexes
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_org_id", "org_id"),
        Index("ix_users_role", "role"),
        Index("ix_users_department_id", "department_id"),
    )
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, role={self.role})>"
