"""Event processing service."""
import logging
import json
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.namespaces.events.schemas import (
    EventPayload,
    StatePayload,
    CommandPayload
)
from src.repositories.mapping_repo import MappingRepository
from src.repositories.lamp_repo import LampRepository
from src.repositories.light_repo import LightRepository
from src.repositories.button_event_repo import ButtonEventRepository
from src.services.event_cache import event_cache
from src.services.mqtt_service import mqtt_service
from src.core.config import settings

logger = logging.getLogger(__name__)


class EventService:
    """Service for processing automation events."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mapping_repo = MappingRepository(db)
        self.lamp_repo = LampRepository(db)
        self.light_repo = LightRepository(db)
        self.button_event_repo = ButtonEventRepository(db)
    
    async def process_button_event(self, event: EventPayload) -> Dict:
        """
        Process a button press event from ESP32/Arduino.
        
        Args:
            event: Button event payload
            
        Returns:
            Processing result with actions taken
        """
        logger.info(f"Processing button event: {event.device}/{event.button} -> {event.action}")
        
        # Save button event to database (always, for discovery purposes)
        try:
            await self.button_event_repo.create_event(
                device=event.device,
                button=event.button,
                action=event.action,
                origin="mqtt",  # Events from process_button_event come from MQTT
                rssi=getattr(event, 'rssi', None),
                data_hora=datetime.utcnow()
            )
            logger.debug(f"Button event saved to database: {event.device}/{event.button}/{event.action}")
        except Exception as e:
            logger.error(f"Error saving button event to database: {e}", exc_info=True)
        
        # Check for duplicate event (idempotency)
        event_hash = event_cache.generate_event_hash(
            device=event.device,
            button=event.button,
            action=event.action
        )
        
        if event_cache.is_duplicate(event_hash):
            logger.debug(f"Duplicate event ignored: {event_hash}")
            return {
                "status": "duplicate",
                "message": "Event already processed recently"
            }
        
        # Find matching mappings
        mappings = await self.mapping_repo.find_matching_mappings(
            device=event.device,
            button=event.button,
            action=event.action
        )
        
        if not mappings:
            logger.warning(f"No mappings found for {event.device}/{event.button}/{event.action}")
            return {
                "status": "no_mappings",
                "message": "No automation rules configured for this button"
            }
        
        # Execute each mapping
        results = []
        for mapping in mappings:
            if not mapping.active:
                logger.debug(f"Skipping inactive mapping {mapping.id}")
                continue
            
            try:
                result = await self._execute_mapping(mapping, event)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing mapping {mapping.id}: {e}", exc_info=True)
                results.append({
                    "mapping_id": mapping.id,
                    "status": "error",
                    "error": str(e)
                })
        
        await self.db.commit()
        
        return {
            "status": "processed",
            "event": event.model_dump(),
            "mappings_executed": len(results),
            "results": results
        }
    
    async def _execute_mapping(self, mapping, event: EventPayload) -> Dict:
        """
        Execute a single mapping action.
        
        Args:
            mapping: Mapping object from database
            event: Original event that triggered this mapping
            
        Returns:
            Execution result
        """
        logger.info(f"Executing mapping {mapping.id}: {mapping.target_type}/{mapping.target_id}")
        
        # Parse parameters
        parameters = {}
        if mapping.parameters_json:
            try:
                parameters = json.loads(mapping.parameters_json)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in mapping {mapping.id} parameters")
        
        target_type = mapping.target_type.lower()
        target_id = mapping.target_id
        
        # Resolve lamp name from ID
        lamp_name = await self._resolve_lamp_name(target_id)
        if not lamp_name:
            logger.error(f"Could not resolve lamp name from ID {target_id}")
            return {
                "mapping_id": mapping.id,
                "status": "error",
                "error": f"Lamp ID {target_id} not found"
            }
        
        # Execute based on target type
        if target_type == "lampada_on":
            return await self._turn_on_lamp(lamp_name, origin="automation")
        
        elif target_type == "lampada_off":
            return await self._turn_off_lamp(lamp_name, origin="automation")
        
        elif target_type == "lampada_toggle":
            return await self._toggle_lamp(lamp_name, origin="automation")
        
        elif target_type == "group_on":
            return await self._control_group(lamp_name, True, origin="automation")
        
        elif target_type == "group_off":
            return await self._control_group(lamp_name, False, origin="automation")
        
        else:
            logger.warning(f"Unknown target type: {target_type}")
            return {
                "mapping_id": mapping.id,
                "status": "error",
                "error": f"Unknown target type: {target_type}"
            }
    
    async def _resolve_lamp_name(self, lamp_id: int) -> Optional[str]:
        """
        Resolve lamp name from numeric ID.
        
        Args:
            lamp_id: Numeric lamp ID
            
        Returns:
            Lamp name or None if not found
        """
        try:
            # Try lampada table first (new)
            lamp = await self.lamp_repo.get_by_id(lamp_id)
            if lamp:
                return lamp.nome
            
            # Fallback to luzes table (legacy)
            light = await self.light_repo.get_by_id(lamp_id)
            if light:
                return light.lampada
            
            logger.warning(f"Lamp ID {lamp_id} not found in any table")
            return None
        except Exception as e:
            logger.error(f"Error resolving lamp name from ID {lamp_id}: {e}")
            return None
    
    async def _turn_on_lamp(self, lamp_name: str, origin: str = "automation") -> Dict:
        """Turn on a lamp."""
        try:
            # Try lampada table first (new)
            lamp = await self.lamp_repo.get_by_name(lamp_name)
            if lamp:
                await self.lamp_repo.update_state(lamp_name, True)
            else:
                # Fallback to luzes table (legacy)
                light = await self.light_repo.get_by_name(lamp_name)
                if not light:
                    light = await self.light_repo.create_if_not_exists(lamp_name, True)
                else:
                    await self.light_repo.update_state(lamp_name, True)
            
            # Publish MQTT command
            command = {
                "comodo": lamp_name,
                "acao": "ligar",
                "origem": origin
            }
            await mqtt_service.publish(settings.MQTT_TOPIC_COMMAND, command)
            
            logger.info(f"Lamp {lamp_name} turned ON")
            return {
                "target": lamp_name,
                "action": "turn_on",
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error turning on lamp {lamp_name}: {e}")
            return {
                "target": lamp_name,
                "action": "turn_on",
                "status": "error",
                "error": str(e)
            }
    
    async def _turn_off_lamp(self, lamp_name: str, origin: str = "automation") -> Dict:
        """Turn off a lamp."""
        try:
            # Try lampada table first (new)
            lamp = await self.lamp_repo.get_by_name(lamp_name)
            if lamp:
                await self.lamp_repo.update_state(lamp_name, False)
            else:
                # Fallback to luzes table (legacy)
                light = await self.light_repo.get_by_name(lamp_name)
                if light:
                    await self.light_repo.update_state(lamp_name, False)
            
            # Publish MQTT command
            command = {
                "comodo": lamp_name,
                "acao": "desligar",
                "origem": origin
            }
            await mqtt_service.publish(settings.MQTT_TOPIC_COMMAND, command)
            
            logger.info(f"Lamp {lamp_name} turned OFF")
            return {
                "target": lamp_name,
                "action": "turn_off",
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error turning off lamp {lamp_name}: {e}")
            return {
                "target": lamp_name,
                "action": "turn_off",
                "status": "error",
                "error": str(e)
            }
    
    async def _toggle_lamp(self, lamp_name: str, origin: str = "automation") -> Dict:
        """Toggle a lamp state."""
        try:
            # Check current state
            lamp = await self.lamp_repo.get_by_name(lamp_name)
            if lamp:
                new_state = not lamp.estado
                await self.lamp_repo.update_state(lamp_name, new_state)
            else:
                # Fallback to luzes table
                light = await self.light_repo.get_by_name(lamp_name)
                if not light:
                    # Create with ON state if doesn't exist
                    light = await self.light_repo.create_if_not_exists(lamp_name, True)
                    new_state = True
                else:
                    new_state = not light.estado
                    await self.light_repo.update_state(lamp_name, new_state)
            
            # Publish MQTT command
            command = {
                "comodo": lamp_name,
                "acao": "ligar" if new_state else "desligar",
                "origem": origin
            }
            await mqtt_service.publish(settings.MQTT_TOPIC_COMMAND, command)
            
            logger.info(f"Lamp {lamp_name} toggled to {new_state}")
            return {
                "target": lamp_name,
                "action": "toggle",
                "new_state": new_state,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error toggling lamp {lamp_name}: {e}")
            return {
                "target": lamp_name,
                "action": "toggle",
                "status": "error",
                "error": str(e)
            }
    
    async def _control_group(self, group_name: str, state: bool, origin: str = "automation") -> Dict:
        """Control a group of lamps."""
        # Define light groups (could be moved to database later)
        LIGHT_GROUPS = {
            "sala": ["L_Sala", "L_Mesa"],
            "antessala": ["L_Antessala", "L_mesa", "L_mesa_amarela"],
            "cozinha": ["L_Balcao", "L_Cozinha"],
        }
        
        group_lamps = LIGHT_GROUPS.get(group_name.lower(), [])
        if not group_lamps:
            return {
                "target": group_name,
                "action": "group_control",
                "status": "error",
                "error": f"Unknown group: {group_name}"
            }
        
        results = []
        for lamp_name in group_lamps:
            if state:
                result = await self._turn_on_lamp(lamp_name, origin)
            else:
                result = await self._turn_off_lamp(lamp_name, origin)
            results.append(result)
        
        return {
            "target": group_name,
            "action": "group_control",
            "state": state,
            "lamps_controlled": len(results),
            "results": results,
            "status": "success"
        }
    
    async def process_state_confirmation(self, state: StatePayload) -> Dict:
        """
        Process state confirmation from ESP32/Arduino.
        
        This is when a device confirms it has changed a lamp state.
        We update the database but DON'T trigger new automations
        to prevent loops.
        
        Args:
            state: State confirmation payload
            
        Returns:
            Processing result
        """
        logger.info(f"Processing state confirmation: {state.device}/{state.target} -> {state.state}")
        
        try:
            # Update database state
            new_state = state.state.lower() == "on"
            
            # Try lampada table first
            lamp = await self.lamp_repo.get_by_name(state.target)
            if lamp:
                await self.lamp_repo.update_state(state.target, new_state)
            else:
                # Fallback to luzes table
                light = await self.light_repo.get_by_name(state.target)
                if light:
                    await self.light_repo.update_state(state.target, new_state)
                else:
                    # Create if doesn't exist
                    await self.light_repo.create_if_not_exists(state.target, new_state)
            
            await self.db.commit()
            
            return {
                "status": "success",
                "target": state.target,
                "state": state.state
            }
        except Exception as e:
            logger.error(f"Error processing state confirmation: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
