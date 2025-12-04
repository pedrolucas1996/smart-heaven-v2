"""Schemas for system namespace."""
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
    success: bool = Field(..., description="Whether operation was successful")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "success": True
            }
        }
