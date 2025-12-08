"""Repository for Lamp operations (lampada table)."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.lamp import Lamp
from src.repositories.base import BaseRepository


class LampRepository(BaseRepository[Lamp]):
    """Repository for lamp operations using lampada table."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Lamp, db)
    
    async def get_all_lamps(self) -> List[Lamp]:
        """Get all lamps."""
        result = await self.db.execute(
            select(Lamp).order_by(Lamp.nome)
        )
        return list(result.scalars().all())
    
    async def get_by_name(self, nome: str) -> Optional[Lamp]:
        """Get a lamp by name."""
        result = await self.db.execute(
            select(Lamp).where(Lamp.nome == nome)
        )
        return result.scalar_one_or_none()
    
    async def get_by_base(self, base_id: int) -> List[Lamp]:
        """Get all lamps for a specific base."""
        result = await self.db.execute(
            select(Lamp)
            .where(Lamp.base_id == base_id)
            .order_by(Lamp.nome)
        )
        return list(result.scalars().all())
    
    async def update_state(self, nome: str, estado: bool) -> Optional[Lamp]:
        """Update lamp state by name."""
        lamp = await self.get_by_name(nome)
        if lamp:
            lamp.estado = estado
            await self.db.flush()
        return lamp
    
    async def create_if_not_exists(
        self, 
        nome: str, 
        base_id: int,
        estado: bool = False
    ) -> Lamp:
        """Create a lamp if it doesn't exist."""
        lamp = await self.get_by_name(nome)
        if not lamp:
            lamp = await self.create({
                "nome": nome,
                "base_id": base_id,
                "estado": estado
            })
        return lamp
    
    async def get_by_name_and_base(self, nome: str, base_id: int) -> Optional[Lamp]:
        """Get a lamp by name and base ID."""
        result = await self.db.execute(
            select(Lamp).where(
                and_(
                    Lamp.nome == nome,
                    Lamp.base_id == base_id
                )
            )
        )
        return result.scalar_one_or_none()
