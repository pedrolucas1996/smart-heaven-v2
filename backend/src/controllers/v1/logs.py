"""Logs API endpoints."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_database
from src.schemas import LogResponse
from src.repositories.log_repo import LogRepository

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("", response_model=List[LogResponse])
async def get_logs(
    comodo: Optional[str] = Query(None, description="Filter by light name"),
    origem: Optional[str] = Query(None, description="Filter by origin"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_database)
):
    """
    Get event logs with optional filtering.
    
    - **comodo**: Filter by light name
    - **origem**: Filter by origin (api, web, botao, esp_mqtt, etc.)
    - **start_date**: Filter from date
    - **end_date**: Filter until date
    - **limit**: Maximum number of results (1-1000)
    - **offset**: Pagination offset
    """
    repo = LogRepository(db)
    
    if comodo:
        logs = await repo.get_logs_by_light(comodo, limit, offset)
    elif origem:
        logs = await repo.get_logs_by_origin(origem, limit, offset)
    elif start_date and end_date:
        logs = await repo.get_logs_by_date_range(start_date, end_date, limit, offset)
    else:
        logs = await repo.get_recent_logs(limit)
    
    return logs


@router.get("/recent", response_model=List[LogResponse])
async def get_recent_logs(
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_database)
):
    """
    Get most recent logs.
    
    - **limit**: Number of recent logs to retrieve (1-500)
    """
    repo = LogRepository(db)
    logs = await repo.get_recent_logs(limit)
    return logs


@router.get("/light/{comodo}", response_model=List[LogResponse])
async def get_logs_by_light(
    comodo: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_database)
):
    """
    Get logs for a specific light.
    
    - **comodo**: Light name
    - **limit**: Number of results
    - **offset**: Pagination offset
    """
    repo = LogRepository(db)
    logs = await repo.get_logs_by_light(comodo, limit, offset)
    return logs
