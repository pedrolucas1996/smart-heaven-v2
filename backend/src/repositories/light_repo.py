"""Repository for Light operations."""
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Light
from src.repositories.base import BaseRepository


class LightRepository(BaseRepository[Light]):
    """Repository for light/lamp operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Light, db)
    
    async def get_by_name(self, lampada: str) -> Optional[Light]:
        """Get a light by its name."""
        result = await self.db.execute(
            select(Light)
            .where(Light.lampada == lampada)
            .order_by(Light.id.desc())  # Get most recent if duplicates exist
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_all_lights(self) -> List[Light]:
        """Get all lights."""
        result = await self.db.execute(select(Light))
        return list(result.scalars().all())
    
    async def update_state(self, lampada: str, estado: bool) -> Optional[Light]:
        """Update light state by name."""
        await self.db.execute(
            update(Light)
            .where(Light.lampada == lampada)
            .values(estado=estado)
        )
        await self.db.flush()
        return await self.get_by_name(lampada)
    
    async def create_if_not_exists(self, lampada: str, estado: bool = False) -> Light:
        """Create a light if it doesn't exist."""
        existing = await self.get_by_name(lampada)
        if existing:
            return existing
        
        return await self.create({"lampada": lampada, "estado": estado})
    
    async def get_lights_by_state(self, estado: bool) -> List[Light]:
        """Get all lights with a specific state."""
        result = await self.db.execute(
            select(Light).where(Light.estado == estado)
        )
        return list(result.scalars().all())
