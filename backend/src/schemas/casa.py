from pydantic import BaseModel, Field
from typing import Optional

class CasaBase(BaseModel):
    estado: str = Field(..., min_length=2, max_length=2)
    cidade: str
    bairro: str
    rua: str
    numero: str
    complemento: Optional[str] = None
    cep: str
    plano: str

class CasaCreate(CasaBase):
    pass

class CasaUpdate(BaseModel):
    estado: Optional[str] = None
    cidade: Optional[str] = None
    bairro: Optional[str] = None
    rua: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    cep: Optional[str] = None
    plano: Optional[str] = None

class CasaResponse(CasaBase):
    id: int
    id_house: int
    class Config:
        from_attributes = True
