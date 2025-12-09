"""Schemas for event system with MQTT payloads.

Supports both modern standardized format (v1.0) and legacy formats for gradual migration.

Examples:
    Modern button event:
        {
            "v": "1.0",
            "device": "Base_D",
            "type": "button",
            "button": "S1",
            "action": "press",
            "rssi": -60,
            "origin": "esp",
            "ts": "2025-12-08T11:23:00Z"
        }
    
    State confirmation:
        {
            "v": "1.0",
            "comodo": "L_Cozinha",
            "state": "ON",
            "origin": "Base_C",
            "ts": "2025-12-08T11:23:02Z"
        }
    
    Command (server -> device):
        {
            "v": "1.0",
            "comodo": "L_Cozinha",
            "command": "toggle",
            "origin": "server",
            "trigger": "Base_D_S1_press",
            "ts": "2025-12-08T11:23:03Z"
        }
    
    Legacy state (ESP-01 local action):
        {
            "comodo": "L_Churrasqueira",
            "state": "ON",
            "ts": "2025-12-08T11:11:00"
        }
"""
from datetime import datetime
from typing import Optional, Literal, Any, Dict
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class EventType(str, Enum):
    """Event type enumeration."""
    BUTTON = "button"
    SWITCH = "switch"
    SENSOR = "sensor"


class ButtonAction(str, Enum):
    """Button action enumeration."""
    PRESS = "press"
    RELEASE = "release"
    CHANGED = "changed"


class LightState(str, Enum):
    """Light state enumeration."""
    ON = "ON"
    OFF = "OFF"


class CommandType(str, Enum):
    """Command type enumeration."""
    ON = "on"
    OFF = "off"
    TOGGLE = "toggle"
    PULSE_SEQUENCE = "pulse_sequence"


class Origin(str, Enum):
    """Message origin enumeration."""
    ESP = "esp"
    SERVER = "server"
    WEB = "web"
    API = "api"


# ===== Modern Format Schemas (v1.0) =====

class EventPayload(BaseModel):
    """
    Modern standardized event payload (device -> broker -> backend).
    
    Devices send events, backend decides actions and publishes commands.
    """
    v: str = Field(default="1.0", description="Protocol version")
    device: str = Field(..., description="Source device identifier (e.g., Base_D, Base_A)")
    type: EventType = Field(..., description="Event type: button, switch, or sensor")
    button: str = Field(..., description="Button/switch identifier (e.g., S1, S2)")
    action: ButtonAction = Field(..., description="Action performed: press, release, changed")
    rssi: Optional[int] = Field(None, description="WiFi signal strength (optional)")
    origin: Origin = Field(default=Origin.ESP, description="Event origin")
    ts: datetime = Field(..., description="Event timestamp (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "v": "1.0",
                "device": "Base_D",
                "type": "button",
                "button": "S1",
                "action": "press",
                "rssi": -60,
                "origin": "esp",
                "ts": "2025-12-08T11:23:00Z"
            }
        }


class StatePayload(BaseModel):
    """
    State confirmation payload (device confirms action).
    
    Published by device after executing command to confirm state change.
    """
    v: str = Field(default="1.0", description="Protocol version")
    comodo: str = Field(..., description="Light/device identifier")
    state: LightState = Field(..., description="Current state: ON or OFF")
    origin: str = Field(..., description="Device that performed action")
    ts: datetime = Field(..., description="State change timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "v": "1.0",
                "comodo": "L_Cozinha",
                "state": "ON",
                "origin": "Base_C",
                "ts": "2025-12-08T11:23:02Z"
            }
        }


class CommandPayload(BaseModel):
    """
    Command payload (backend -> device).
    
    Backend publishes commands after processing events and applying mappings.
    """
    v: str = Field(default="1.0", description="Protocol version")
    comodo: str = Field(..., description="Target light/device")
    command: CommandType = Field(..., description="Command: on, off, toggle")
    origin: Origin = Field(default=Origin.SERVER, description="Command origin (always server)")
    trigger: Optional[str] = Field(None, description="Event that triggered this command")
    ts: datetime = Field(default_factory=datetime.utcnow, description="Command timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "v": "1.0",
                "comodo": "L_Cozinha",
                "command": "toggle",
                "origin": "server",
                "trigger": "Base_D_S1_press",
                "ts": "2025-12-08T11:23:03Z"
            }
        }


class GateCommandPayload(BaseModel):
    """
    Special command for gate control (pulse sequence).
    
    Target: BASE_Portao device.
    """
    command: Literal["pulse_sequence"] = Field(..., description="Command type")
    pulses: int = Field(..., ge=1, le=20, description="Number of pulses")
    pulse_ms: int = Field(..., ge=100, le=5000, description="Pulse duration in milliseconds")
    origin: Origin = Field(default=Origin.SERVER, description="Command origin")
    v: str = Field(default="1.0", description="Protocol version")
    ts: datetime = Field(default_factory=datetime.utcnow, description="Command timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "command": "pulse_sequence",
                "pulses": 8,
                "pulse_ms": 1000,
                "origin": "server",
                "v": "1.0"
            }
        }


# ===== Legacy Format Schemas =====

class LegacyStatePayload(BaseModel):
    """
    Legacy state payload (old ESP-01 and similar devices).
    
    These devices actuate locally and publish state without version field.
    Backend adapts these to modern EventPayload format.
    """
    comodo: str = Field(..., description="Light identifier")
    state: str = Field(..., description="State: ON or OFF")
    ts: Optional[str] = Field(None, description="Timestamp (may be missing or non-ISO)")
    
    @field_validator('state')
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Normalize state to uppercase."""
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "comodo": "L_Churrasqueira",
                "state": "ON",
                "ts": "2025-12-08T11:11:00"
            }
        }


# ===== Response Schemas =====

class EventResponse(BaseModel):
    """Response after processing an event."""
    event_id: str = Field(..., description="Unique event identifier")
    received_ts: datetime = Field(..., description="When backend received event")
    processed: bool = Field(..., description="Whether event was processed successfully")
    mappings_applied: int = Field(..., description="Number of mappings applied")
    commands_published: int = Field(..., description="Number of commands published")
    actions: list[Dict[str, Any]] = Field(default_factory=list, description="Actions executed")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "Base_D_S1_press_2025-12-08T11:23:00Z",
                "received_ts": "2025-12-08T11:23:00.123Z",
                "processed": True,
                "mappings_applied": 1,
                "commands_published": 1,
                "actions": [
                    {
                        "target": "L_Cozinha",
                        "command": "toggle",
                        "topic": "casa/servidor/comando_lampada"
                    }
                ]
            }
        }


class MappingBase(BaseModel):
    """Base mapping schema."""
    source_device: str = Field(..., description="Source device (e.g., Base_D)")
    source_button: str = Field(..., description="Button identifier (e.g., S1, * for wildcard)")
    source_action: Optional[str] = Field("press", description="Button action (press, release, changed, * for any)")
    action_type: str = Field(..., description="Action to perform (e.g., toggle_light, turn_on, turn_off)")
    target_type: str = Field(..., description="Target type (light, gate, scene, script)")
    target_id: str = Field(..., description="Target identifier (comodo name, scene id)")
    parameters_json: Optional[Dict[str, Any]] = Field(None, description="Additional parameters (JSON)")
    priority: int = Field(100, description="Execution priority (lower = higher priority)")
    description: Optional[str] = Field(None, description="Human-readable description")


class MappingResponse(MappingBase):
    """Mapping configuration response."""
    id: int
    active: bool = Field(default=True, description="Whether mapping is active")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MappingCreate(MappingBase):
    """Create new mapping."""
    active: bool = True


class MappingUpdate(BaseModel):
    """Update existing mapping."""
    source_device: Optional[str] = None
    source_button: Optional[str] = None
    source_action: Optional[str] = None
    action_type: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    parameters_json: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class MetricsResponse(BaseModel):
    """System metrics response."""
    total_events: int = Field(..., description="Total events received")
    events_processed: int = Field(..., description="Successfully processed events")
    events_failed: int = Field(..., description="Failed events")
    commands_published: int = Field(..., description="Commands published to MQTT")
    average_latency_ms: float = Field(..., description="Average processing latency")
    uptime_seconds: float = Field(..., description="Backend uptime")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_events": 1523,
                "events_processed": 1520,
                "events_failed": 3,
                "commands_published": 1520,
                "average_latency_ms": 45.2,
                "uptime_seconds": 86400.0
            }
        }
