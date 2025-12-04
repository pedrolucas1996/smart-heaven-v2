"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============================================
# Light Schemas
# ============================================

class LightBase(BaseModel):
    """Base light schema."""
    lampada: str = Field(..., min_length=1, max_length=50, description="Light name/identifier")


class LightCreate(LightBase):
    """Schema for creating a light."""
    estado: bool = Field(default=False, description="Initial state")


class LightUpdate(BaseModel):
    """Schema for updating a light."""
    estado: Optional[bool] = Field(None, description="New state")


class LightResponse(LightBase):
    """Schema for light response."""
    id: int
    estado: bool
    data_de_atualizacao: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LightCommand(BaseModel):
    """Schema for light command."""
    comodo: str = Field(..., description="Light name")
    acao: str = Field(..., pattern="^(ligar|desligar)$", description="Action: ligar or desligar")
    origem: str = Field(default="api", description="Command origin")


# ============================================
# Switch Schemas
# ============================================

class SwitchBase(BaseModel):
    """Base switch schema."""
    nome: str = Field(..., min_length=1, max_length=50, description="Switch name")
    base: str = Field(..., min_length=1, max_length=50, description="Base/Board name")


class SwitchCreate(SwitchBase):
    """Schema for creating a switch."""
    ativo: bool = Field(default=True, description="Enabled/Disabled")


class SwitchUpdate(BaseModel):
    """Schema for updating a switch."""
    ativo: Optional[bool] = Field(None, description="Enable/Disable switch")
    estado: Optional[bool] = Field(None, description="Physical button state")


class SwitchResponse(SwitchBase):
    """Schema for switch response."""
    id: int
    estado: bool
    ativo: bool
    data_de_atualizacao: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SwitchCommand(BaseModel):
    """Schema for switch enable/disable command."""
    botao: str = Field(..., description="Switch name")
    acao: str = Field(..., pattern="^(habilitar|desabilitar)$", description="Action")


# ============================================
# Log Schemas
# ============================================

class LogCreate(BaseModel):
    """Schema for creating a log entry."""
    comodo: str = Field(..., description="Light name")
    estado: bool = Field(..., description="State")
    origem: str = Field(..., description="Origin of the event")
    detalhes: Optional[str] = Field(None, description="Additional details")


class LogResponse(BaseModel):
    """Schema for log response."""
    id: int
    comodo: str
    estado: bool
    origem: str
    timestamp: datetime
    detalhes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class LogFilter(BaseModel):
    """Schema for log filtering."""
    comodo: Optional[str] = None
    origem: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ============================================
# Light Group Schemas
# ============================================

class LightGroupBase(BaseModel):
    """Base light group schema."""
    nome: str = Field(..., min_length=1, max_length=50)
    descricao: Optional[str] = Field(None, max_length=200)
    lampadas: List[str] = Field(..., min_items=1, description="List of light names")


class LightGroupCreate(LightGroupBase):
    """Schema for creating a light group."""
    ativo: bool = Field(default=True)


class LightGroupUpdate(BaseModel):
    """Schema for updating a light group."""
    descricao: Optional[str] = None
    lampadas: Optional[List[str]] = None
    ativo: Optional[bool] = None


class LightGroupResponse(LightGroupBase):
    """Schema for light group response."""
    id: int
    ativo: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# MQTT Event Schemas
# ============================================

class ButtonEvent(BaseModel):
    """Schema for button event from MQTT."""
    base: str
    botao: str
    estado: str = Field(..., pattern="^(pressionado|solto)$")
    t_inicio: Optional[int] = None


class MQTTStateUpdate(BaseModel):
    """Schema for MQTT state update."""
    comodo: str
    estado: str = Field(..., pattern="^(on|off)$")


# ============================================
# WebSocket Schemas
# ============================================

class WSMessage(BaseModel):
    """WebSocket message schema."""
    type: str = Field(..., description="Message type")
    data: dict = Field(..., description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Generic Response Schemas
# ============================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    mqtt_connected: bool
    database_connected: bool


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True
