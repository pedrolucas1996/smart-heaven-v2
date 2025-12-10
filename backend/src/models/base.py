"""Base model for hardware bases (ESP32, Arduino, etc)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship

from src.infra.db import Base


class HardwareBase(Base):
    """Hardware base model (ESP32, Arduino Mega, etc)."""
    
    __tablename__ = "base"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        
    id_house = Column(Integer, nullable=False)
    nome = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relationships
    switches = relationship("Switch", back_populates="base", cascade="all, delete-orphan")
    lamps = relationship("Lamp", back_populates="base", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HardwareBase(id={self.id}, nome='{self.nome}')>"
