"""System controller (health check, cleanup, and root)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.controllers.deps import get_database, get_mqtt_service
from src.core.config import settings
from src.namespaces.system.schemas import HealthResponse, MessageResponse
from src.services.cleanup_service import CleanupService

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


@router.get("/stats", response_model=dict)
async def get_database_stats(db: AsyncSession = Depends(get_database)):
    """
    Get database statistics.
    
    Returns statistics about logs and lights tables including:
    - Total records
    - Date ranges
    - Duplicate information
    """
    service = CleanupService(db)
    
    log_stats = await service.get_logs_statistics()
    light_stats = await service.get_lights_statistics()
    
    return {
        "logs": log_stats,
        "lights": light_stats
    }


@router.post("/cleanup/logs", response_model=MessageResponse)
async def cleanup_logs(
    days: int = None,
    limit: int = None,
    db: AsyncSession = Depends(get_database)
):
    """
    Clean old log records.
    
    - **days**: Delete logs older than N days (optional)
    - **limit**: Keep only N most recent logs (optional)
    
    At least one parameter must be provided.
    """
    if not days and not limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify 'days' or 'limit' parameter"
        )
    
    service = CleanupService(db)
    total_deleted = 0
    
    if days:
        deleted = await service.cleanup_old_logs(days)
        total_deleted += deleted
    
    if limit:
        deleted = await service.cleanup_logs_by_limit(limit)
        total_deleted += deleted
    
    return MessageResponse(
        message=f"Successfully deleted {total_deleted} log records"
    )


@router.post("/cleanup/lights", response_model=MessageResponse)
async def cleanup_duplicate_lights(db: AsyncSession = Depends(get_database)):
    """
    Remove duplicate entries in lights table.
    
    Keeps only the most recent record for each unique light name.
    """
    service = CleanupService(db)
    deleted = await service.cleanup_duplicate_lights()
    
    return MessageResponse(
        message=f"Successfully deleted {deleted} duplicate light records"
    )
