"""Schemas for lamps namespace (lampada table)."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class LampBase(BaseModel):
    """Base schema for lamp data."""
    nome: str = Field(..., description="Lamp name/identifier")


class LampCreate(LampBase):
    """Schema for creating a new lamp."""
    base_id: int = Field(..., description="Base ID this lamp belongs to")
    estado: bool = Field(default=False, description="Initial state (on/off)")
    invertido: bool = Field(default=False, description="Hardware inverted signal")


class LampUpdate(BaseModel):
    """Schema for updating a lamp."""
    nome: Optional[str] = Field(None, description="Lamp name")
    base_id: Optional[int] = Field(None, description="Base ID")
    estado: Optional[bool] = Field(None, description="State (on/off)")
    invertido: Optional[bool] = Field(None, description="Hardware inverted signal")


class LampResponse(LampBase):
    """Schema for lamp response."""
    id: int = Field(..., description="Lamp ID")
    base_id: int = Field(..., description="Base ID")
    estado: bool = Field(..., description="Current state (on/off)")
    invertido: bool = Field(..., description="Hardware inverted signal")
    data_de_atualizacao: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class LampCommand(BaseModel):
    """Schema for lamp control commands."""
    nome: str = Field(..., description="Lamp name")
    acao: str = Field(..., description="Action: 'ligar' or 'desligar'")
    origem: str = Field(default="api", description="Command origin")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nome": "L_Sala",
                "acao": "ligar",
                "origem": "web"
            }
        }
