from sqlalchemy import Column, Integer, String
from src.infra.db import Base

class Casa(Base):
    __tablename__ = 'casa'
    id = Column(Integer, primary_key=True, autoincrement=True)
    estado = Column(String(2), nullable=False)
    cidade = Column(String(100), nullable=False)
    bairro = Column(String(100), nullable=False)
    rua = Column(String(100), nullable=False)
    numero = Column(String(20), nullable=False)
    complemento = Column(String(100), nullable=True)
    cep = Column(String(20), nullable=False)
    id_user = Column(Integer, nullable=False)
    nome = Column(String(50), nullable=False)
    plano = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Casa(id={self.id}, cidade='{self.cidade}', rua='{self.rua}', numero='{self.numero}')>"
