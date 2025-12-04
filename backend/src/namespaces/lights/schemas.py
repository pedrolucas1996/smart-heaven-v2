"""Schemas for lights namespace."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class LightBase(BaseModel):
    """Base schema for light data."""
    lampada: str = Field(..., description="Light name/identifier")


class LightCreate(LightBase):
    """Schema for creating a new light."""
    estado: bool = Field(default=False, description="Initial state (on/off)")


class LightUpdate(BaseModel):
    """Schema for updating a light."""
    estado: Optional[bool] = Field(None, description="New state (on/off)")


class LightResponse(LightBase):
    """Schema for light response."""
    estado: bool = Field(..., description="Current state (on/off)")
    data_de_atualizacao: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class LightCommand(BaseModel):
    """Schema for light control commands."""
    comodo: str = Field(..., description="Light name")
    acao: str = Field(..., description="Action: 'ligar' or 'desligar'")
    origem: str = Field(default="api", description="Command origin")
    
    class Config:
        json_schema_extra = {
            "example": {
                "comodo": "sala",
                "acao": "ligar",
                "origem": "web"
            }
        }
