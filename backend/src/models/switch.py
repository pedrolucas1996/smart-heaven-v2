"""Switch/Button model."""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship

from src.infra.db import Base


class Switch(Base):
    """Switch/Button model."""
    
    __tablename__ = "interruptor"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base_id = Column(Integer, ForeignKey("base.id", ondelete="CASCADE"), nullable=False, index=True)
    nome = Column(String(50), nullable=False, index=True)
    estado = Column(Boolean, default=False, nullable=False, comment="Physical button state")
    ativo = Column(Boolean, default=True, nullable=False, comment="Enabled/Disabled")
    data_de_atualizacao = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    base = relationship("HardwareBase", back_populates="switches")
    lamp_mappings = relationship("SwitchLampMapping", back_populates="switch", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_base_nome', 'base_id', 'nome'),
    )
    
    def __repr__(self):
        return f"<Switch(id={self.id}, nome='{self.nome}', base_id={self.base_id}, ativo={self.ativo})>"
