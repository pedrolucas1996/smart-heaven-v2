from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.casa import Casa

class CasaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(Casa))
        return result.scalars().all()

    async def get_by_id(self, casa_id: int):
        result = await self.db.execute(select(Casa).where(Casa.id == casa_id))
        return result.scalar_one_or_none()

    async def create(self, data: dict):
        casa = Casa(**data)
        self.db.add(casa)
        await self.db.flush()
        return casa

    async def update(self, casa_id: int, data: dict):
        casa = await self.get_by_id(casa_id)
        if not casa:
            return None
        for key, value in data.items():
            setattr(casa, key, value)
        await self.db.flush()
        return casa

    async def delete(self, casa_id: int):
        casa = await self.get_by_id(casa_id)
        if not casa:
            return False
        await self.db.delete(casa)
        await self.db.flush()
        return True
