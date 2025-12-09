"""Event log model."""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Index, Text, BigInteger
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship

from src.infra.db import Base


class Log(Base):
    """Event log model."""
    
    __tablename__ = "logs"
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True, autoincrement=True)
    comodo = Column(String(50), ForeignKey("luzes.lampada"), nullable=False, index=True)
    estado = Column(Boolean, nullable=False)
    origem = Column(String(50), nullable=False, index=True)
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    light = relationship("Light", back_populates="logs")
    
    __table_args__ = (
        Index('idx_data_comodo', 'data_hora', 'comodo'),
    )
    
    def __repr__(self):
        return f"<Log(comodo='{self.comodo}', estado={self.estado}, origem='{self.origem}')>"
