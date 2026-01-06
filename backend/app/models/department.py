"""
Tarento AI Complaint Tracking System - Department Model
"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base, TimestampMixin

class Department(Base, TimestampMixin):
    """Department model for strict role assignments"""
    
    __tablename__ = "departments"
    
    department_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False
    )
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    manager_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Relationships
    organization = relationship("Organization", back_populates="departments")
    manager = relationship(
        "User", 
        foreign_keys=[manager_id],
        back_populates="managed_department"
    )
    users = relationship(
        "User", 
        foreign_keys="User.department_id",
        back_populates="department_link"
    )
    projects = relationship("Project", back_populates="department")
    
    def __repr__(self):
        return f"<Department(department_id={self.department_id}, name={self.name})>"
