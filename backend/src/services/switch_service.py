"""Switch control service with business logic."""
import json
import logging
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.switch_repo import SwitchRepository
from src.services.mqtt_service import mqtt_service
from src.services.light_service import LightService

logger = logging.getLogger(__name__)

# Switch to light mappings from original system
SWITCH_LIGHT_MAPPING = {
    ("Base_A_banheiro", "S_Banheirosuite"): ["L_Banheirosuite"],
    ("Base_A", "S_Banheirosuite_1"): ["L_Banheirosuite"],
    ("Base_A", "S_Suite1_1"): ["L_Suite"],
    ("Base_A", "S_Suite1_2"): ["L_Sala"],
    ("Base_A", "S_Sala_1"): ["L_Entrada"],
    ("Base_A", "S_Sala_2"): ["L_Sala"],
    ("Base_A", "S_Sala_3"): ["L_Quarto"],
    ("Base_A", "S_Sala2_1"): ["ventilador"],
    ("Base_A", "S_Quarto_1"): ["L_Quarto"],
    ("Base_A", "S_Quarto_2"): ["L_Lavanderia"],
    ("Base_A", "S_Lavanderia_1"): ["L_Lavanderia"],
    ("Base_A", "S_Lavanderia_2"): ["L_Entrada"],
    ("Base_B", "S_Entrada_1"): ["L_Entrada"],
    ("Base_B", "S_Entrada_2"): ["L_Garagem"],
    ("Base_B", "S_Entrada_3"): ["L_Antessala"],
    ("Base_B", "S_Entrada_4"): ["L_Cozinha", "L_Balcao"],
    ("Base_B", "S_Garagem_1"): ["L_Garagem"],
    ("Base_B", "S_Garagem_2"): ["L_Holofote"],
    ("Base_B", "S_Garagem_3"): ["L_Jardim"],
    ("Base_B1", "S_Entrada"): ["L_Entrada"],
    ("Base_B1", "S_Garagem"): ["L_Garagem"],
    ("Base_B1", "S_Antessala"): ["L_Antessala"],
    ("Base_B1", "S_CozinhaGeral"): ["L_CozinhaGeral"],
    ("Base_C1", "S_Churrasqueira"): ["L_Churrasqueira"],
    ("Base_A1", "S_Lavanderia"): ["L_Lavanderia"],
    ("Base_A1", "S_Entrada"): ["L_Entrada"],
    ("Base_A1", "S_Sala"): ["L_Sala"],
    ("Base_A1", "S_Quarto"): ["L_Quarto"],
    ("Base_D", "S_Lavanderia_PIR"): ["L_Lavanderia"],
    ("Base_D", "S_Escritorio"): ["L_Escritorio"],
    ("Base_D", "S_Banheirogeral"): ["L_Banheirogeral"]
}

# Add Base_C switches
for i in range(1, 7):
    mapping = {
        1: ["L_Entrada"],
        2: ["L_Garagem"],
        3: ["L_Antessala"],
        4: ["L_Cozinha"],
        5: ["L_Balcao"],
        6: ["L_Holofote"]
    }
    SWITCH_LIGHT_MAPPING[("Base_C", f"S_Caixa_{i}")] = mapping[i]


class SwitchService:
    """Service for switch control operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.switch_repo = SwitchRepository(db)
        self.light_counters: Dict[str, int] = {}
    
    async def get_all_switches(self) -> List:
        """Get all switches."""
        return await self.switch_repo.get_all_switches()
    
    async def get_switch_by_name(self, nome: str) -> Optional:
        """Get a specific switch by name."""
        return await self.switch_repo.get_by_name(nome)
    
    async def enable_switch(self, nome: str) -> dict:
        """Enable a switch."""
        switch = await self.switch_repo.update_active_state(nome, True)
        await self.db.commit()
        
        if switch:
            await mqtt_service.publish_debug(f"[Servidor] Botao {switch.base}/{nome} habilitado")
            return {"nome": nome, "ativo": True, "message": "Switch enabled"}
        
        return {"error": "Switch not found"}
    
    async def disable_switch(self, nome: str) -> dict:
        """Disable a switch."""
        switch = await self.switch_repo.update_active_state(nome, False)
        await self.db.commit()
        
        if switch:
            await mqtt_service.publish_debug(f"[Servidor] Botao {switch.base}/{nome} desabilitado")
            return {"nome": nome, "ativo": False, "message": "Switch disabled"}
        
        return {"error": "Switch not found"}
    
    async def handle_button_event(self, topic: str, payload: str):
        """Handle button press events from MQTT."""
        try:
            evento = json.loads(payload)
            base = evento.get("base")
            botao = evento.get("botao")
            estado = evento.get("estado")
            
            if not all([base, botao, estado]):
                logger.warning("Incomplete button event")
                return
            
            # Check if switch is enabled
            switch = await self.switch_repo.get_by_base_and_name(base, botao)
            if not switch:
                # Create switch if it doesn't exist
                switch = await self.switch_repo.create_if_not_exists(botao, base)
                await self.db.commit()
            
            if not switch.ativo:
                logger.info(f"Switch {base}/{botao} is disabled. Ignoring.")
                return
            
            # Update physical state
            if estado in ["pressionado", "solto"]:
                await self.switch_repo.update_physical_state(botao, estado == "pressionado")
                await self.db.commit()
            
            # Handle button press
            if estado == "pressionado":
                await self._handle_button_press(base, botao)
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in button event: {payload}")
        except Exception as e:
            logger.error(f"Error handling button event: {e}")
    
    async def _handle_button_press(self, base: str, botao: str):
        """Handle button press logic."""
        mapping_key = (base, botao)
        
        if mapping_key not in SWITCH_LIGHT_MAPPING:
            logger.warning(f"No mapping found for {base}/{botao}")
            return
        
        lights = SWITCH_LIGHT_MAPPING[mapping_key]
        light_service = LightService(self.db)
        
        # Special case for Base_B S_Entrada_4
        if mapping_key == ("Base_B", "S_Entrada_4"):
            # Check if both lights are off
            all_off = True
            for light_name in lights:
                light = await light_service.get_light_by_name(light_name)
                if light and light.estado:
                    all_off = False
                    break
            
            # Turn all on if all off, otherwise turn all off
            new_state = all_off
            for light_name in lights:
                await light_service._control_light(light_name, new_state, "botao")
        else:
            # Toggle each light
            for light_name in lights:
                await light_service.toggle_light(light_name, "botao")
        
        await self.db.commit()
