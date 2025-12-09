"""Legacy adapter for ESP-01 and old devices.

Converts legacy MQTT message formats to modern EventPayload/StatePayload schemas.
Enables gradual migration without requiring firmware updates on all devices.

Legacy formats supported:
    1. Simple state messages (ESP-01 local action):
       {"comodo": "L_Churrasqueira", "state": "ON"}
    
    2. Old button events (if any):
       {"device": "ESP_BaseA", "botao": "B1", "acao": "press"}
    
    3. Raw string payloads:
       "L_Sala:ON"
"""
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import logging

from src.namespaces.events.schemas import (
    EventPayload,
    StatePayload,
    EventType,
    ButtonAction,
    LightState,
    Origin
)

logger = logging.getLogger(__name__)


class LegacyAdapter:
    """
    Adapter for converting legacy device messages to modern schemas.
    
    Detects legacy formats and converts them to EventPayload or StatePayload.
    This enables backward compatibility without changing device firmware.
    """
    
    # Known legacy devices (ESP-01 and similar)
    LEGACY_DEVICES = {
        "ESP_Churrasqueira": "ESP-01",
        "ESP_Varanda": "ESP-01",
        "ESP_Garagem": "ESP-01",
        # Add more as needed
    }
    
    @staticmethod
    def is_legacy_format(payload: Dict[str, Any]) -> bool:
        """
        Detect if payload is in legacy format.
        
        Legacy indicators:
        - No 'v' (version) field
        - Has 'comodo' field (old Portuguese naming)
        - Has 'botao' or 'acao' fields (old naming)
        
        Args:
            payload: Parsed JSON payload
            
        Returns:
            True if legacy format detected
        """
        if not isinstance(payload, dict):
            return True  # Raw strings are legacy
        
        # Modern format always has version field
        if "v" in payload:
            return False
        
        # Legacy Portuguese field names
        legacy_fields = {"comodo", "botao", "acao", "estado"}
        has_legacy_fields = any(field in payload for field in legacy_fields)
        
        return has_legacy_fields
    
    @staticmethod
    def detect_message_type(payload: Dict[str, Any]) -> str:
        """
        Detect what type of legacy message this is.
        
        Returns:
            "state" - State confirmation message
            "button" - Button press event
            "unknown" - Cannot determine
        """
        # Check if it's a button event first (has base + botao + estado)
        # This is the format: {"base":"Base_A1","botao":"S_Entrada","estado":"pressionado"}
        if ("base" in payload or "device" in payload) and ("botao" in payload or "button" in payload):
            return "button"
        
        # If has estado/state but also has comodo, it's a lamp state
        if ("state" in payload or "estado" in payload) and "comodo" in payload:
            return "state"
        
        # Generic action field indicates button
        if "action" in payload or "acao" in payload:
            return "button"
        
        return "unknown"
    
    @classmethod
    def convert_to_state_payload(
        cls,
        payload: Dict[str, Any],
        topic: Optional[str] = None
    ) -> StatePayload:
        """
        Convert legacy state message to modern StatePayload.
        
        Legacy format examples:
            {"comodo": "L_Churrasqueira", "state": "ON"}
            {"comodo": "L_Sala", "estado": "OFF", "ts": "2025-12-08T11:11:00"}
        
        Args:
            payload: Legacy message data
            topic: MQTT topic (helps identify device)
            
        Returns:
            Modern StatePayload
            
        Example:
            >>> legacy = {"comodo": "L_Sala", "state": "ON"}
            >>> adapter = LegacyAdapter()
            >>> modern = adapter.convert_to_state_payload(legacy)
            >>> print(modern.comodo)  # "L_Sala"
            >>> print(modern.state)   # LightState.ON
        """
        # Extract comodo (light name)
        comodo = payload.get("comodo", "unknown")
        
        # Extract state (handle both 'state' and 'estado')
        state_raw = payload.get("state", payload.get("estado", "OFF"))
        state = LightState.ON if state_raw.upper() == "ON" else LightState.OFF
        
        # Extract or infer origin device
        origin = cls._infer_origin_device(payload, topic)
        
        # Extract timestamp or use current time
        ts = cls._parse_timestamp(payload.get("ts"))
        
        return StatePayload(
            v="1.0",
            comodo=comodo,
            state=state,
            origin=origin,
            ts=ts
        )
    
    @classmethod
    def convert_to_event_payload(
        cls,
        payload: Dict[str, Any],
        topic: Optional[str] = None
    ) -> EventPayload:
        """
        Convert legacy button event to modern EventPayload.
        
        Legacy format examples:
            {"base": "Base_A1", "botao": "S_Entrada", "estado": "pressionado"}
            {"device": "ESP_BaseA", "botao": "B1", "acao": "press"}
            {"dispositivo": "Base_C", "button": "S2"}
        
        Args:
            payload: Legacy message data
            topic: MQTT topic (helps identify device)
            
        Returns:
            Modern EventPayload
            
        Example:
            >>> legacy = {"base": "Base_A1", "botao": "S_Entrada", "estado": "pressionado"}
            >>> adapter = LegacyAdapter()
            >>> modern = adapter.convert_to_event_payload(legacy)
            >>> print(modern.device)  # "Base_A1"
            >>> print(modern.button)  # "S_Entrada"
        """
        # Extract device name (check base, device, dispositivo)
        device = payload.get(
            "base",
            payload.get("device", payload.get("dispositivo", cls._infer_device_from_topic(topic)))
        )
        
        # Extract button (handle both English and Portuguese)
        button = payload.get("button", payload.get("botao", "unknown"))
        
        # Extract action (handle multiple formats)
        # Format 1: {"acao": "press"} or {"action": "press"}
        # Format 2: {"estado": "pressionado"} or {"estado": "solto"}
        action_raw = payload.get("action", payload.get("acao"))
        
        if not action_raw:
            # Check estado field (Portuguese format from ESP devices)
            estado = payload.get("estado", "")
            if estado == "pressionado":
                action_raw = "press"
            elif estado == "solto":
                action_raw = "release"
            else:
                action_raw = "press"  # Default
        
        try:
            action = ButtonAction(action_raw.lower())
        except ValueError:
            action = ButtonAction.PRESS
        
        # Extract timestamp
        ts = cls._parse_timestamp(payload.get("ts"))
        
        return EventPayload(
            v="1.0",
            device=device,
            type=EventType.BUTTON,
            button=button,
            action=action,
            rssi=None,
            origin=Origin.ESP,
            ts=ts
        )
    
    @classmethod
    def convert_legacy_message(
        cls,
        payload: Dict[str, Any],
        topic: Optional[str] = None
    ) -> Tuple[str, Any]:
        """
        Automatically detect and convert any legacy message.
        
        Args:
            payload: Legacy message data
            topic: MQTT topic
            
        Returns:
            Tuple of (message_type, converted_payload)
            message_type: "state" or "event"
            converted_payload: StatePayload or EventPayload
            
        Raises:
            ValueError: If message type cannot be determined
            
        Example:
            >>> legacy = {"comodo": "L_Sala", "state": "ON"}
            >>> msg_type, modern = LegacyAdapter.convert_legacy_message(legacy)
            >>> print(msg_type)  # "state"
            >>> print(isinstance(modern, StatePayload))  # True
        """
        msg_type = cls.detect_message_type(payload)
        
        if msg_type == "state":
            return ("state", cls.convert_to_state_payload(payload, topic))
        
        elif msg_type == "button":
            return ("event", cls.convert_to_event_payload(payload, topic))
        
        else:
            logger.warning(f"Unknown legacy message format: {payload}")
            raise ValueError(f"Cannot convert unknown legacy format: {payload}")
    
    @staticmethod
    def _infer_origin_device(
        payload: Dict[str, Any],
        topic: Optional[str]
    ) -> str:
        """
        Infer the origin device from payload or topic.
        
        Strategies:
        1. Check 'device' or 'dispositivo' in payload
        2. Extract from MQTT topic path
        3. Check 'comodo' and map to known device
        4. Default to "ESP-01_Legacy"
        """
        # Direct device field
        if "device" in payload:
            return payload["device"]
        if "dispositivo" in payload:
            return payload["dispositivo"]
        
        # Extract from topic (e.g., "casa/estado/lampada/Base_A")
        if topic:
            parts = topic.split("/")
            if len(parts) >= 4:
                return parts[-1]  # Last segment often is device
        
        # Map comodo to device (if known)
        comodo = payload.get("comodo", "")
        if comodo in LegacyAdapter.LEGACY_DEVICES:
            return LegacyAdapter.LEGACY_DEVICES[comodo]
        
        # Default
        return "ESP-01_Legacy"
    
    @staticmethod
    def _infer_device_from_topic(topic: Optional[str]) -> str:
        """Extract device name from MQTT topic."""
        if not topic:
            return "unknown"
        
        parts = topic.split("/")
        # Try to find a part that looks like a device name
        for part in parts:
            if "base" in part.lower() or "esp" in part.lower():
                return part
        
        return parts[-1] if parts else "unknown"
    
    @staticmethod
    def _parse_timestamp(ts: Optional[str]) -> datetime:
        """
        Parse timestamp from legacy format.
        
        Handles:
        - ISO 8601: "2025-12-08T11:23:00Z"
        - Simple format: "2025-12-08T11:23:00"
        - Missing/invalid: use current time
        """
        if not ts:
            return datetime.utcnow()
        
        try:
            # Try ISO format with Z
            if ts.endswith("Z"):
                return datetime.fromisoformat(ts[:-1])
            # Try ISO format without Z
            return datetime.fromisoformat(ts)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid timestamp format: {ts}, using current time")
            return datetime.utcnow()
    
    @classmethod
    def parse_raw_string_payload(cls, raw: str) -> Dict[str, Any]:
        """
        Parse raw string payloads (very old devices).
        
        Formats supported:
            "L_Sala:ON"
            "Base_A,B1,press"
            "L_Cozinha,OFF"
        
        Args:
            raw: Raw string payload
            
        Returns:
            Parsed dictionary
            
        Example:
            >>> LegacyAdapter.parse_raw_string_payload("L_Sala:ON")
            {'comodo': 'L_Sala', 'state': 'ON'}
        """
        # Format: "L_Sala:ON"
        if ":" in raw:
            parts = raw.split(":")
            if len(parts) == 2:
                return {"comodo": parts[0].strip(), "state": parts[1].strip()}
        
        # Format: "Base_A,B1,press"
        if "," in raw:
            parts = [p.strip() for p in raw.split(",")]
            if len(parts) == 3:
                return {
                    "device": parts[0],
                    "button": parts[1],
                    "action": parts[2]
                }
            elif len(parts) == 2:
                return {"comodo": parts[0], "state": parts[1]}
        
        # Cannot parse
        logger.error(f"Cannot parse raw string payload: {raw}")
        return {"raw": raw}
