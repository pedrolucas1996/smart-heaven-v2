"""Light model (luzes table - legacy/compatibility)."""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, BigInteger
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from src.infra.db import Base


class Light(Base):
    """Light/Lamp model (luzes table - legacy table for backward compatibility)."""
    
    __tablename__ = "luzes"
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True, autoincrement=True)
    lampada = Column(String(50), unique=True, nullable=False, index=True)
    estado = Column(Boolean, default=False, nullable=False)
    data_de_atualizacao = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    logs = relationship("Log", back_populates="light", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Light(lampada='{self.lampada}', estado={self.estado})>"
