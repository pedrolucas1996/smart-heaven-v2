"""Repository for Switch operations."""
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Switch
from src.repositories.base import BaseRepository


class SwitchRepository(BaseRepository[Switch]):
    """Repository for switch/button operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Switch, db)
    
    async def get_by_name(self, nome: str) -> Optional[Switch]:
        """Get a switch by its name."""
        result = await self.db.execute(
            select(Switch).where(Switch.nome == nome)
        )
        return result.scalar_one_or_none()
    
    async def get_by_base_and_name(self, base: str, nome: str) -> Optional[Switch]:
        """Get a switch by base and name."""
        result = await self.db.execute(
            select(Switch).where(
                Switch.base == base,
                Switch.nome == nome
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_switches(self) -> List[Switch]:
        """Get all switches."""
        result = await self.db.execute(
            select(Switch).options(joinedload(Switch.base))
        )
        return list(result.scalars().all())
    
    async def get_by_base(self, base: str) -> List[Switch]:
        """Get all switches for a specific base."""
        result = await self.db.execute(
            select(Switch).where(Switch.base == base)
        )
        return list(result.scalars().all())
    
    async def update_active_state(self, nome: str, ativo: bool) -> Optional[Switch]:
        """Enable or disable a switch."""
        await self.db.execute(
            update(Switch)
            .where(Switch.nome == nome)
            .values(ativo=ativo)
        )
        await self.db.flush()
        return await self.get_by_name(nome)
    
    async def update_physical_state(self, nome: str, estado: bool) -> Optional[Switch]:
        """Update the physical state of a switch."""
        await self.db.execute(
            update(Switch)
            .where(Switch.nome == nome)
            .values(estado=estado)
        )
        await self.db.flush()
        return await self.get_by_name(nome)
    
    async def get_active_switches(self) -> List[Switch]:
        """Get all active (enabled) switches."""
        result = await self.db.execute(
            select(Switch).where(Switch.ativo == True)
        )
        return list(result.scalars().all())
    
    async def create_if_not_exists(
        self, 
        nome: str, 
        base: str, 
        ativo: bool = True
    ) -> Switch:
        """Create a switch if it doesn't exist."""
        existing = await self.get_by_base_and_name(base, nome)
        if existing:
            return existing
        
        return await self.create({
            "nome": nome,
            "base": base,
            "estado": False,
            "ativo": ativo
        })
