"""Button event log model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.dialects.mysql import BIGINT

from src.infra.db import Base


class ButtonEvent(Base):
    """Button/switch event log model.
    
    Tracks all button presses from ESP32/Arduino devices.
    Useful for debugging, automation discovery, and activity monitoring.
    """
    
    __tablename__ = "button_events"
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True, autoincrement=True)
        
    id_house = Column(Integer, nullable=True, default=1)
    
    # Event identification
    device = Column(String(50), nullable=False, index=True, comment="Device identifier (e.g., Base_D, Base_A)")
    button = Column(String(50), nullable=False, index=True, comment="Button identifier (e.g., S1, B2)")
    action = Column(String(20), nullable=False, default="press", comment="Action: press, release, changed")
    
    # Metadata
    origin = Column(String(50), nullable=True, comment="Event origin (mqtt, api, etc)")
    rssi = Column(Integer, nullable=True, comment="WiFi signal strength (optional)")
    
    # Timestamp
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="When event occurred")
    
    __table_args__ = (
        Index('idx_device_button_hora', 'device', 'button', 'data_hora'),
        Index('idx_device_hora', 'device', 'data_hora'),
    )
    
    def __repr__(self):
        return f"<ButtonEvent(device='{self.device}', button='{self.button}', action='{self.action}', ts={self.data_hora})>"
