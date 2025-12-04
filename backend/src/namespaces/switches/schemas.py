"""Schemas for switches namespace."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class SwitchBase(BaseModel):
    """Base schema for switch data."""
    nome: str = Field(..., description="Switch name/identifier")


class SwitchCreate(SwitchBase):
    """Schema for creating a new switch."""
    base: str = Field(..., description="Hardware base name (e.g., 'base_A', 'base_B')")
    ativo: bool = Field(default=True, description="Whether the switch is enabled")


class SwitchUpdate(BaseModel):
    """Schema for updating a switch."""
    ativo: Optional[bool] = Field(None, description="Enable/disable switch")
    estado: Optional[bool] = Field(None, description="Physical button state")


class SwitchResponse(SwitchBase):
    """Schema for switch response."""
    base: str = Field(..., description="Hardware base name")
    estado: bool = Field(..., description="Current physical button state")
    ativo: bool = Field(..., description="Whether switch is enabled")
    data_de_atualizacao: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SwitchCommand(BaseModel):
    """Schema for switch control commands."""
    botao: str = Field(..., description="Switch name")
    acao: str = Field(..., description="Action: 'habilitar' or 'desabilitar'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "botao": "interruptor_sala_1",
                "acao": "habilitar"
            }
        }
