"""SQLAlchemy models for Smart Heaven.

Import all models here to ensure they're registered with SQLAlchemy.
"""
from src.models.base import HardwareBase
from src.models.switch import Switch
from src.models.lamp import Lamp
from src.models.light import Light
from src.models.switch_lamp_mapping import SwitchLampMapping
from src.models.log import Log

__all__ = [
    "HardwareBase",
    "Switch",
    "Lamp",
    "Light",
    "SwitchLampMapping",
    "Log",
]
