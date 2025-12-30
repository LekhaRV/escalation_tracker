"""
Tarento AI Complaint Tracking System - Agent Log Model
Complete audit trail for AI agents
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import uuid

from app.database import Base, TimestampMixin
from app.utils.constants import AgentLogStatus


class AgentLog(Base, TimestampMixin):
    """Agent Log model - audit trail for all AI agent executions"""
    
    __tablename__ = "agent_logs"
    
    log_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    agent_name = Column(String(100), nullable=False)  # email_parser, categorization, etc.
    complaint_id = Column(
        UUID(as_uuid=True),
        ForeignKey("complaints.complaint_id", ondelete="SET NULL"),
        nullable=True  # Some agents may not be complaint-specific
    )
    
    # Execution data
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    execution_time_ms = Column(Integer)  # Execution duration in milliseconds
    
    # Status
    status = Column(
        SQLEnum(AgentLogStatus, name="agent_log_status"),
        nullable=False
    )
    error_message = Column(Text)  # Error details if failed
    
    # Timestamp
    executed_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    complaint = relationship("Complaint", back_populates="agent_logs")
    
    # Indexes
    __table_args__ = (
        Index("ix_al_agent_name", "agent_name"),
        Index("ix_al_complaint_id", "complaint_id"),
        Index("ix_al_status", "status"),
        Index("ix_al_executed_at", "executed_at"),
    )
    
    def __repr__(self):
        return f"<AgentLog(log_id={self.log_id}, agent={self.agent_name}, status={self.status})>"
