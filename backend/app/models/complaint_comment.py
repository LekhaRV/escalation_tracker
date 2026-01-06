"""
Tarento AI Complaint Tracking System - Complaint Comment Model
Internal notes and comments on complaints
"""

from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.database import Base


class ComplaintComment(Base):
    """Internal comments/notes on complaints"""
    __tablename__ = "complaint_comments"

    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.complaint_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    complaint = relationship("Complaint", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ComplaintComment {self.comment_id}>"
