"""Repository for event-to-action mappings."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.mapping import Mapping


class MappingRepository:
    """Repository for managing event mappings."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Mapping:
        """Create a new mapping."""
        mapping = Mapping(**data)
        self.db.add(mapping)
        await self.db.flush()
        await self.db.refresh(mapping)
        return mapping
    
    async def get_by_id(self, mapping_id: int) -> Optional[Mapping]:
        """Get mapping by ID."""
        result = await self.db.execute(
            select(Mapping).where(Mapping.id == mapping_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, active_only: bool = False) -> List[Mapping]:
        """Get all mappings."""
        query = select(Mapping)
        if active_only:
            query = query.where(Mapping.active == True)
        query = query.order_by(Mapping.priority, Mapping.id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_device(
        self,
        device: str,
        active_only: bool = True
    ) -> List[Mapping]:
        """Get all mappings for a specific device."""
        query = select(Mapping).where(Mapping.source_device == device)
        if active_only:
            query = query.where(Mapping.active == True)
        query = query.order_by(Mapping.priority, Mapping.id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def find_matching_mappings(
        self,
        device: str,
        button: str,
        action: str
    ) -> List[Mapping]:
        """
        Find all active mappings that match the given event.
        
        Supports wildcards in button and action fields.
        Returns mappings ordered by priority.
        
        Args:
            device: Source device identifier
            button: Button identifier
            action: Button action
            
        Returns:
            List of matching active mappings
        """
        # Get all active mappings for this device
        all_mappings = await self.get_by_device(device, active_only=True)
        
        # Filter using the model's matches_event method
        matching = [
            m for m in all_mappings
            if m.matches_event(device, button, action)
        ]
        
        return matching
    
    async def update(
        self,
        mapping_id: int,
        data: Dict[str, Any]
    ) -> Optional[Mapping]:
        """Update a mapping."""
        mapping = await self.get_by_id(mapping_id)
        if not mapping:
            return None
        
        for key, value in data.items():
            if hasattr(mapping, key) and value is not None:
                setattr(mapping, key, value)
        
        await self.db.flush()
        await self.db.refresh(mapping)
        return mapping
    
    async def delete(self, mapping_id: int) -> bool:
        """Delete a mapping."""
        mapping = await self.get_by_id(mapping_id)
        if not mapping:
            return False
        
        await self.db.delete(mapping)
        await self.db.flush()
        return True
    
    async def deactivate(self, mapping_id: int) -> Optional[Mapping]:
        """Deactivate a mapping (soft delete)."""
        return await self.update(mapping_id, {"active": False})
    
    async def activate(self, mapping_id: int) -> Optional[Mapping]:
        """Activate a mapping."""
        return await self.update(mapping_id, {"active": True})
    
    async def get_by_target(
        self,
        target_type: str,
        target_id: str,
        active_only: bool = True
    ) -> List[Mapping]:
        """Get all mappings that target a specific entity."""
        query = select(Mapping).where(
            Mapping.target_type == target_type,
            Mapping.target_id == target_id
        )
        if active_only:
            query = query.where(Mapping.active == True)
        query = query.order_by(Mapping.priority, Mapping.id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_active(self) -> int:
        """Count active mappings."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).select_from(Mapping).where(Mapping.active == True)
        )
        return result.scalar() or 0
