"""Lamp control service using lampada table."""
import json
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.lamp_repo import LampRepository
from src.repositories.log_repo import LogRepository
from src.services.mqtt_service import mqtt_service
from src.core.config import settings

logger = logging.getLogger(__name__)

# Light groupings from original system
LIGHT_GROUPS = {
    "L_Antessala": ["L_mesa", "L_mesa_amarela"],
    "L_CozinhaGeral": ["L_Balcao", "L_Cozinha"]
}


class LampService:
    """Service for lamp control operations using lampada table."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lamp_repo = LampRepository(db)
        self.log_repo = LogRepository(db)
    
    async def get_lamps_by_house(self, id_house: int) -> List:
        """Get all lamps for a specific house."""
        return await self.lamp_repo.get_by_house(id_house)
    
    async def get_lamp_by_name(self, nome: str) -> Optional:
        """Get a specific lamp by name."""
        return await self.lamp_repo.get_by_name(nome)
    
    async def get_lamps_by_base(self, base_id: int) -> List:
        """Get all lamps for a specific base."""
        return await self.lamp_repo.get_by_base(base_id)
    
    async def turn_on_lamp(self, nome: str, origem: str = "api") -> dict:
        """Turn on a lamp."""
        return await self._control_lamp(nome, True, origem)
    
    async def turn_off_lamp(self, nome: str, origem: str = "api") -> dict:
        """Turn off a lamp."""
        return await self._control_lamp(nome, False, origem)
    
    async def toggle_lamp(self, nome: str, origem: str = "api") -> dict:
        """Toggle a lamp."""
        lamp = await self.lamp_repo.get_by_name(nome)
        if not lamp:
            raise ValueError(f"Lamp {nome} not found")
        
        new_state = not lamp.estado
        return await self._control_lamp(nome, new_state, origem)
    
    async def _control_lamp(
        self, 
        nome: str, 
        estado: bool, 
        origem: str
    ) -> dict:
        """Internal method to control a lamp."""
        nome = nome.strip()
        
        # Update database
        lamp = await self.lamp_repo.get_by_name(nome)
        if not lamp:
            raise ValueError(f"Lamp {nome} not found. Please create it first with a base_id.")
        
        lamp = await self.lamp_repo.update_state(nome, estado)
        
        # Create log
        await self.log_repo.create_log(nome, estado, origem, lamp.id_house)
        
        # Prepare MQTT command
        acao = "ligar" if estado else "desligar"
        mqtt_payload = {"comodo": nome, "acao": acao}
        
        # Determine the correct MQTT topic
        if nome == "L_Portao":
            topic = settings.MQTT_TOPIC_ESP_COMMAND
        elif nome in ["L_Jardim", "L_Escritorio", "L_Banheirogeral", "LED_Azul", "LED_Bancada"]:
            topic = settings.MQTT_TOPIC_COMMAND
        else:
            topic = settings.MQTT_TOPIC_COMMAND
        
        # Publish to MQTT
        try:
            await mqtt_service.publish(topic, mqtt_payload)
            await mqtt_service.publish_state(nome, "on" if estado else "off")
            logger.info(f"Lamp {nome} turned {acao} via {origem}")
        except Exception as e:
            logger.error(f"Failed to publish MQTT command for {nome}: {e}")
        
        # Handle grouped lights
        if nome in LIGHT_GROUPS:
            for grouped_lamp in LIGHT_GROUPS[nome]:
                try:
                    await self._control_lamp(
                        grouped_lamp, 
                        estado, 
                        f"{origem} (grupo {nome})"
                    )
                except ValueError:
                    logger.warning(f"Grouped lamp {grouped_lamp} not found")
        
        await self.db.commit()
        
        return {
            "nome": nome,
            "estado": estado,
            "acao": acao,
            "origem": origem
        }
    
    async def handle_mqtt_state_update(self, topic: str, payload: str):
        """Handle MQTT state updates from devices."""
        try:
            nome = topic.split("/")[-1]
            estado_str = payload.strip().lower()
            
            if estado_str not in ["on", "off"]:
                logger.warning(f"Invalid state payload: {payload}")
                return
            
            estado = estado_str == "on"
            
            # Update database
            lamp = await self.lamp_repo.update_state(nome, estado)
            if lamp:
                await self.log_repo.create_log(nome, estado, "esp_mqtt", lamp.id_house)
                await self.db.commit()
                logger.info(f"State updated from MQTT: {nome} = {estado}")
            else:
                logger.warning(f"Lamp {nome} not found for state update")
            
        except Exception as e:
            logger.error(f"Error handling MQTT state update: {e}")
    
    async def handle_web_command(self, topic: str, payload: str):
        """Handle commands from web interface via MQTT."""
        try:
            comando = json.loads(payload)
            nome = comando.get("comodo") or comando.get("nome")
            valor = comando.get("valor")
            acao = comando.get("acao")
            
            if not nome:
                logger.warning("Missing nome/comodo in web command")
                return
            
            # Determine action
            if acao:
                estado = acao == "ligar"
            elif valor is not None:
                estado = bool(valor)
            else:
                logger.warning("Missing action or value in web command")
                return
            
            # Control the lamp
            await self._control_lamp(nome, estado, "web")
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in web command: {payload}")
        except Exception as e:
            logger.error(f"Error handling web command: {e}")
    
    async def create_lamp(self, nome: str, base_id: int, estado: bool = False, comodo: str = None) -> dict:
        """Create a new lamp."""
        lamp = await self.lamp_repo.create({
            "nome": nome,
            "base_id": base_id,
            "estado": estado,
            "comodo": comodo
        })
        await self.db.commit()
        return lamp
    
    async def update_lamp(self, lamp_id: int, **kwargs) -> Optional:
        """Update a lamp."""
        lamp = await self.lamp_repo.update(lamp_id, kwargs)
        if lamp:
            await self.db.commit()
        return lamp
    
    async def delete_lamp(self, lamp_id: int) -> bool:
        """Delete a lamp."""
        success = await self.lamp_repo.delete(lamp_id)
        if success:
            await self.db.commit()
        return success
