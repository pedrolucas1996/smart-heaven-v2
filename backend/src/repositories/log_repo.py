"""Repository for Log operations."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Log
from src.repositories.base import BaseRepository


class LogRepository(BaseRepository[Log]):
    """Repository for event log operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Log, db)
    
    async def create_log(
        self,
        comodo: str,
        estado: bool,
        origem: str
    ) -> Log:
        """Create a new log entry."""
        return await self.create({
            "comodo": comodo,
            "estado": estado,
            "origem": origem
        })
    
    async def get_logs_by_light(
        self,
        comodo: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Log]:
        """Get logs for a specific light."""
        result = await self.db.execute(
            select(Log)
            .where(Log.comodo == comodo)
            .order_by(desc(Log.data_hora))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_logs_by_origin(
        self,
        origem: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Log]:
        """Get logs by origin."""
        result = await self.db.execute(
            select(Log)
            .where(Log.origem == origem)
            .order_by(desc(Log.data_hora))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_logs_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0
    ) -> List[Log]:
        """Get logs within a date range."""
        result = await self.db.execute(
            select(Log)
            .where(
                Log.data_hora >= start_date,
                Log.data_hora <= end_date
            )
            .order_by(desc(Log.data_hora))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_recent_logs(self, limit: int = 50) -> List[Log]:
        """Get most recent logs."""
        result = await self.db.execute(
            select(Log)
            .order_by(desc(Log.data_hora))
            .limit(limit)
        )
        return list(result.scalars().all())
