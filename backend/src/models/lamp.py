"""Lamp model (lampada table)."""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship

from src.infra.db import Base


class Lamp(Base):
    """Lamp model (lampada table with base relationship)."""
    
    __tablename__ = "lampada"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base_id = Column(Integer, ForeignKey("base.id", ondelete="CASCADE"), nullable=False, index=True)
    nome = Column(String(50), nullable=False, index=True)
    apelido = Column(String(50), nullable=True)
    estado = Column(Boolean, default=False, nullable=False)
    invertido = Column(Boolean, default=False, nullable=False)
    comodo = Column(String(50), nullable=True)
    data_de_atualizacao = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    
    # Relationships
    base = relationship("HardwareBase", back_populates="lamps")
    switch_mappings = relationship("SwitchLampMapping", back_populates="lamp", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_base_nome', 'base_id', 'nome'),
    )
    
    def __repr__(self):
        return f"<Lamp(id={self.id}, nome='{self.nome}', estado={self.estado})>"
