"""System controller (health check, cleanup, metrics, and root)."""
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func, and_

from src.controllers.deps import get_database, get_mqtt_service
from src.core.config import settings
from src.namespaces.system.schemas import HealthResponse, MessageResponse, MetricsResponse
from src.services.cleanup_service import CleanupService
from src.models.logs import Log
from src.models.lampada import Lampada
from src.models.mapping import Mapping

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


@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics(db: AsyncSession = Depends(get_database)):
    """
    Get comprehensive system metrics.
    
    Returns real-time statistics including:
    - Event counts (total logs, recent activity)
    - Mapping configuration (active/inactive)
    - Lamp states (on/off/total)
    - Recent activity (last 24h, 7 days, 30 days)
    - System uptime information
    
    Useful for dashboards and monitoring.
    """
    # Get total events (logs)
    total_logs_result = await db.execute(select(func.count()).select_from(Log))
    total_events = total_logs_result.scalar() or 0
    
    # Get recent activity (last 24h)
    last_24h = datetime.now() - timedelta(days=1)
    recent_logs_result = await db.execute(
        select(func.count()).select_from(Log).where(Log.data_hora >= last_24h)
    )
    events_last_24h = recent_logs_result.scalar() or 0
    
    # Get recent activity (last 7 days)
    last_7d = datetime.now() - timedelta(days=7)
    week_logs_result = await db.execute(
        select(func.count()).select_from(Log).where(Log.data_hora >= last_7d)
    )
    events_last_7d = week_logs_result.scalar() or 0
    
    # Get recent activity (last 30 days)
    last_30d = datetime.now() - timedelta(days=30)
    month_logs_result = await db.execute(
        select(func.count()).select_from(Log).where(Log.data_hora >= last_30d)
    )
    events_last_30d = month_logs_result.scalar() or 0
    
    # Get mapping counts
    total_mappings_result = await db.execute(select(func.count()).select_from(Mapping))
    total_mappings = total_mappings_result.scalar() or 0
    
    active_mappings_result = await db.execute(
        select(func.count()).select_from(Mapping).where(Mapping.active == True)
    )
    active_mappings = active_mappings_result.scalar() or 0
    
    # Get lamp states
    total_lamps_result = await db.execute(select(func.count()).select_from(Lampada))
    total_lamps = total_lamps_result.scalar() or 0
    
    # Count lamps by state (ON/OFF)
    on_lamps_result = await db.execute(
        select(func.count()).select_from(Lampada).where(Lampada.estado == "ligar")
    )
    lamps_on = on_lamps_result.scalar() or 0
    
    off_lamps_result = await db.execute(
        select(func.count()).select_from(Lampada).where(Lampada.estado == "desligar")
    )
    lamps_off = off_lamps_result.scalar() or 0
    
    # Get most active lamps (top 5 by log count in last 7 days)
    most_active_query = await db.execute(
        select(Log.nome, func.count(Log.id).label("count"))
        .where(Log.data_hora >= last_7d)
        .group_by(Log.nome)
        .order_by(func.count(Log.id).desc())
        .limit(5)
    )
    most_active_lamps = [
        {"name": row[0], "events": row[1]}
        for row in most_active_query.all()
    ]
    
    # Get latest event timestamp
    latest_event_result = await db.execute(
        select(func.max(Log.data_hora)).select_from(Log)
    )
    latest_event = latest_event_result.scalar()
    
    # MQTT connection status
    mqtt = get_mqtt_service()
    mqtt_connected = mqtt.is_connected
    
    return MetricsResponse(
        timestamp=datetime.now(),
        total_events=total_events,
        events_last_24h=events_last_24h,
        events_last_7d=events_last_7d,
        events_last_30d=events_last_30d,
        total_mappings=total_mappings,
        active_mappings=active_mappings,
        inactive_mappings=total_mappings - active_mappings,
        total_lamps=total_lamps,
        lamps_on=lamps_on,
        lamps_off=lamps_off,
        most_active_lamps=most_active_lamps,
        latest_event=latest_event,
        mqtt_connected=mqtt_connected,
        database_connected=True
    )

