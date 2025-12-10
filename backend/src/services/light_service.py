"""Light control service with business logic."""
import json
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.light_repo import LightRepository
from src.repositories.log_repo import LogRepository
from src.services.mqtt_service import mqtt_service
from src.core.config import settings

logger = logging.getLogger(__name__)

# Light groupings from original system
LIGHT_GROUPS = {
    "L_Antessala": ["L_mesa", "L_mesa_amarela"],
    "L_CozinhaGeral": ["L_Balcao", "L_Cozinha"]
}


class LightService:
    """Service for light control operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.light_repo = LightRepository(db)
        self.log_repo = LogRepository(db)
    
    async def get_all_lights(self) -> List:
        """Get all lights."""
        return await self.light_repo.get_all_lights()
    
    async def get_lights_by_house(self, id_house: int) -> List:
        """Get all lights for a specific house."""
        return await self.light_repo.get_by_house(id_house)
    
    async def get_light_by_name(self, lampada: str) -> Optional:
        """Get a specific light by name."""
        return await self.light_repo.get_by_name(lampada)
    
    async def turn_on_light(self, comodo: str, origem: str = "api") -> dict:
        """Turn on a light."""
        return await self._control_light(comodo, True, origem)
    
    async def turn_off_light(self, comodo: str, origem: str = "api") -> dict:
        """Turn off a light."""
        return await self._control_light(comodo, False, origem)
    
    async def toggle_light(self, comodo: str, origem: str = "api") -> dict:
        """Toggle a light."""
        light = await self.light_repo.get_by_name(comodo)
        if not light:
            light = await self.light_repo.create_if_not_exists(comodo)
        
        new_state = not light.estado
        return await self._control_light(comodo, new_state, origem)
    
    async def _control_light(
        self, 
        comodo: str, 
        estado: bool, 
        origem: str
    ) -> dict:
        """Internal method to control a light."""
        comodo = comodo.strip()
        
        # Update database
        light = await self.light_repo.get_by_name(comodo)
        if not light:
            light = await self.light_repo.create_if_not_exists(comodo, estado)
        else:
            light = await self.light_repo.update_state(comodo, estado)
        
        # Create log
        await self.log_repo.create_log(comodo, estado, origem, light.id_house)
        
        # Prepare MQTT command
        acao = "ligar" if estado else "desligar"
        mqtt_payload = {"comodo": comodo, "acao": acao}
        
        # Determine the correct MQTT topic
        if comodo == "L_Portao":
            topic = settings.MQTT_TOPIC_ESP_COMMAND
        elif comodo in ["L_Jardim", "L_Escritorio", "L_Banheirogeral", "LED_Azul", "LED_Bancada"]:
            topic = settings.MQTT_TOPIC_COMMAND
        else:
            topic = settings.MQTT_TOPIC_COMMAND
        
        # Publish to MQTT
        try:
            await mqtt_service.publish(topic, mqtt_payload)
            await mqtt_service.publish_state(comodo, "on" if estado else "off")
            logger.info(f"Light {comodo} turned {acao} via {origem}")
        except Exception as e:
            logger.error(f"Failed to publish MQTT command for {comodo}: {e}")
        
        # Handle grouped lights
        if comodo in LIGHT_GROUPS:
            for grouped_light in LIGHT_GROUPS[comodo]:
                await self._control_light(
                    grouped_light, 
                    estado, 
                    f"{origem} (grupo {comodo})"
                )
        
        await self.db.commit()
        
        return {
            "comodo": comodo,
            "estado": estado,
            "acao": acao,
            "origem": origem
        }
    
    async def handle_mqtt_state_update(self, topic: str, payload: str):
        """Handle MQTT state updates from devices."""
        try:
            comodo = topic.split("/")[-1]
            estado_str = payload.strip().lower()
            
            if estado_str not in ["on", "off"]:
                logger.warning(f"Invalid state payload: {payload}")
                return
            
            estado = estado_str == "on"
            
            # Update database
            light = await self.light_repo.update_state(comodo, estado)
            await self.log_repo.create_log(comodo, estado, "esp_mqtt", light.id_house)
            await self.db.commit()
            
            logger.info(f"State updated from MQTT: {comodo} = {estado}")
            
        except Exception as e:
            logger.error(f"Error handling MQTT state update: {e}")
    
    async def handle_web_command(self, topic: str, payload: str):
        """Handle commands from web interface via MQTT."""
        try:
            comando = json.loads(payload)
            comodo = comando.get("comodo")
            valor = comando.get("valor")
            acao = comando.get("acao")
            
            if not comodo:
                logger.warning("Missing comodo in web command")
                return
            
            # Determine action
            if acao:
                estado = acao == "ligar"
            elif valor is not None:
                estado = bool(valor)
            else:
                logger.warning("Missing action or value in web command")
                return
            
            # Control the light
            await self._control_light(comodo, estado, "web")
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in web command: {payload}")
        except Exception as e:
            logger.error(f"Error handling web command: {e}")
