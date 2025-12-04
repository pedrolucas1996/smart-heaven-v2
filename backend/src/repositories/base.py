"""Base repository with common CRUD operations."""
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with generic CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """Get all records with pagination."""
        query = select(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, obj_in: dict) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        """Update a record."""
        await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
        )
        await self.db.flush()
        return await self.get_by_id(id)
    
    async def delete(self, id: int) -> bool:
        """Delete a record."""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.flush()
        return result.rowcount > 0
    
    async def exists(self, **filters) -> bool:
        """Check if a record exists."""
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
