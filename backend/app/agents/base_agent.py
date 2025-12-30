"""
Tarento AI Complaint Tracking System - Base Agent
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AgentLog
from app.utils.constants import AgentLogStatus
from app.core.logging import logger


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, db: AsyncSession, org_id: Optional[UUID] = None):
        self.db = db
        self.org_id = org_id
        self.agent_name = self.__class__.__name__.lower().replace("agent", "")
    
    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """Execute the agent's main logic"""
        pass
    
    async def run(self) -> AgentLog:
        """Run the agent with logging and error handling"""
        start_time = time.time()
        input_data = {"org_id": str(self.org_id) if self.org_id else None}
        
        try:
            logger.info(f"Starting agent: {self.agent_name}")
            result = await self.execute()
            execution_time = int((time.time() - start_time) * 1000)
            
            log = AgentLog(
                agent_name=self.agent_name,
                input_data=input_data,
                output_data=result,
                execution_time_ms=execution_time,
                status=AgentLogStatus.SUCCESS
            )
            
            logger.info(f"Agent {self.agent_name} completed in {execution_time}ms")
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            log = AgentLog(
                agent_name=self.agent_name,
                input_data=input_data,
                output_data={},
                execution_time_ms=execution_time,
                status=AgentLogStatus.FAILURE,
                error_message=str(e)
            )
            
            logger.error(f"Agent {self.agent_name} failed: {str(e)}")
        
        self.db.add(log)
        await self.db.flush()
        
        return log
