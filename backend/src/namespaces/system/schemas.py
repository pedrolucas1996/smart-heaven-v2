"""Schemas for system namespace."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(..., description="System status: 'healthy' or 'degraded'")
    version: str = Field(..., description="API version")
    mqtt_connected: bool = Field(..., description="MQTT broker connection status")
    database_connected: bool = Field(..., description="Database connection status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "mqtt_connected": True,
                "database_connected": True
            }
        }


class MessageResponse(BaseModel):
    """Schema for generic message response."""
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Whether operation was successful")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "success": True
            }
        }


class MetricsResponse(BaseModel):
    """
    System metrics response for monitoring and dashboards.
    
    Provides comprehensive statistics about:
    - Event activity (logs)
    - Automation mappings
    - Lamp states and usage
    - System connectivity
    """
    timestamp: datetime = Field(..., description="Metrics collection timestamp")
    
    # Event statistics
    total_events: int = Field(..., description="Total events (logs) in database")
    events_last_24h: int = Field(..., description="Events in last 24 hours")
    events_last_7d: int = Field(..., description="Events in last 7 days")
    events_last_30d: int = Field(..., description="Events in last 30 days")
    
    # Mapping statistics
    total_mappings: int = Field(..., description="Total automation mappings")
    active_mappings: int = Field(..., description="Active mappings")
    inactive_mappings: int = Field(..., description="Inactive mappings")
    
    # Lamp statistics
    total_lamps: int = Field(..., description="Total lamps in system")
    lamps_on: int = Field(..., description="Lamps currently on")
    lamps_off: int = Field(..., description="Lamps currently off")
    
    # Activity insights
    most_active_lamps: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Top 5 most active lamps (by event count last 7 days)"
    )
    latest_event: Optional[datetime] = Field(
        None,
        description="Timestamp of most recent event"
    )
    
    # System health
    mqtt_connected: bool = Field(..., description="MQTT broker connection status")
    database_connected: bool = Field(..., description="Database connection status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-12-08T15:30:00Z",
                "total_events": 15234,
                "events_last_24h": 342,
                "events_last_7d": 2145,
                "events_last_30d": 8932,
                "total_mappings": 12,
                "active_mappings": 10,
                "inactive_mappings": 2,
                "total_lamps": 18,
                "lamps_on": 5,
                "lamps_off": 13,
                "most_active_lamps": [
                    {"name": "L_Sala", "events": 456},
                    {"name": "L_Cozinha", "events": 342},
                    {"name": "L_Escritorio", "events": 289}
                ],
                "latest_event": "2025-12-08T15:29:45Z",
                "mqtt_connected": True,
                "database_connected": True
            }
        }

