"""Repository for ButtonEvent operations."""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.button_event import ButtonEvent
from src.repositories.base import BaseRepository


class ButtonEventRepository(BaseRepository[ButtonEvent]):
    """Repository for button event operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ButtonEvent, db)
    
    async def create_event(
        self,
        device: str,
        button: str,
        action: str = "press",
        origin: Optional[str] = None,
        rssi: Optional[int] = None,
        data_hora: Optional[datetime] = None
    ) -> ButtonEvent:
        """Create a new button event."""
        event = ButtonEvent(
            device=device,
            button=button,
            action=action,
            origin=origin,
            rssi=rssi,
            data_hora=data_hora or datetime.utcnow()
        )
        self.db.add(event)
        await self.db.flush()
        return event
    
    async def get_recent_events(self, limit: int = 50) -> List[ButtonEvent]:
        """Get most recent button events."""
        result = await self.db.execute(
            select(ButtonEvent)
            .order_by(desc(ButtonEvent.data_hora))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_events_by_device(self, device: str, limit: int = 50) -> List[ButtonEvent]:
        """Get events for a specific device."""
        result = await self.db.execute(
            select(ButtonEvent)
            .where(ButtonEvent.device == device)
            .order_by(desc(ButtonEvent.data_hora))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_events_by_button(self, device: str, button: str, limit: int = 50) -> List[ButtonEvent]:
        """Get events for a specific button."""
        result = await self.db.execute(
            select(ButtonEvent)
            .where(
                (ButtonEvent.device == device) & (ButtonEvent.button == button)
            )
            .order_by(desc(ButtonEvent.data_hora))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_events_in_timerange(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 500
    ) -> List[ButtonEvent]:
        """Get events within a time range."""
        result = await self.db.execute(
            select(ButtonEvent)
            .where(
                (ButtonEvent.data_hora >= start_time) &
                (ButtonEvent.data_hora <= end_time)
            )
            .order_by(desc(ButtonEvent.data_hora))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_events_last_hours(self, hours: int = 24, limit: int = 500) -> List[ButtonEvent]:
        """Get events from last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return await self.get_events_in_timerange(cutoff, datetime.utcnow(), limit)
