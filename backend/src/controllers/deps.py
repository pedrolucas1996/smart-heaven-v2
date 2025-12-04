"""API dependencies."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db import get_db
from src.services.mqtt_service import mqtt_service


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async for session in get_db():
        yield session


def get_mqtt_service():
    """Get MQTT service dependency."""
    return mqtt_service
