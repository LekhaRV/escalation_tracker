from typing import Any
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.services.email_service import email_service

router = APIRouter()

class EmailSimulationRequest(BaseModel):
    sender: EmailStr
    subject: str
    content: str

@router.post("/simulate")
async def simulate_email_reception(
    email_req: EmailSimulationRequest,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Simulate receiving an email via IMAP.
    This triggers the full AI processing pipeline (Classification -> Categorization -> Ticket Creation).
    """
    result = await email_service.process_simulated_email(
        subject=email_req.subject,
        content=email_req.content,
        sender=email_req.sender,
        db_session=db
    )
    return result
