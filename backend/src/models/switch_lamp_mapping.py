"""Switch-Lamp mapping model."""
from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from src.infra.db import Base


class SwitchLampMapping(Base):
    """Many-to-many relationship between switches and lamps."""
    
    __tablename__ = "interruptor_lampada"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_house = Column(Integer, nullable=False)
    interruptor_id = Column(Integer, ForeignKey("interruptor.id", ondelete="CASCADE"), nullable=False)
    lampada_id = Column(Integer, ForeignKey("lampada.id", ondelete="CASCADE"), nullable=False)
    ordem = Column(Integer, nullable=True, comment="Order for sequential activation")
    
    # Relationships
    switch = relationship("Switch", back_populates="lamp_mappings")
    lamp = relationship("Lamp", back_populates="switch_mappings")
    
    __table_args__ = (
        Index('idx_switch_lamp', 'interruptor_id', 'lampada_id', unique=True),
    )
    
    def __repr__(self):
        return f"<SwitchLampMapping(switch_id={self.interruptor_id}, lamp_id={self.lampada_id}, ordem={self.ordem})>"
