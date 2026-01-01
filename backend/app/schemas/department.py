"""
Tarento AI Complaint Tracking System - Department Schemas
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# Base Schema
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    manager_id: Optional[UUID] = None

# Request Schemas
class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    manager_id: Optional[UUID] = None

# Response Schemas
class DepartmentResponse(DepartmentBase):
    department_id: UUID
    org_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DepartmentBriefResponse(BaseModel):
    department_id: UUID
    name: str
    
    class Config:
        from_attributes = True
