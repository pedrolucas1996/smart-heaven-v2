"""Health check and system status endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.api.deps import get_database, get_mqtt_service
from src.core.config import settings
from src.schemas import HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_database)
):
    """
    Health check endpoint.
    
    Returns the system status including:
    - API version
    - MQTT connection status
    - Database connection status
    """
    # Check database connection
    db_connected = False
    try:
        await db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        pass
    
    # Check MQTT connection
    mqtt = get_mqtt_service()
    
    return HealthResponse(
        status="healthy" if (db_connected and mqtt.is_connected) else "degraded",
        version=settings.APP_VERSION,
        mqtt_connected=mqtt.is_connected,
        database_connected=db_connected
    )


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "openapi": "/openapi.json"
    }
