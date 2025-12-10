from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.controllers.deps import get_database
from src.schemas.casa import CasaCreate, CasaUpdate, CasaResponse
from src.repositories.casa_repo import CasaRepository
from typing import List

router = APIRouter(prefix="/casas", tags=["Casas"])

@router.get("", response_model=List[CasaResponse])
async def get_all_casas(db: AsyncSession = Depends(get_database)):
    repo = CasaRepository(db)
    return await repo.get_all()

@router.get("/{casa_id}", response_model=CasaResponse)
async def get_casa(casa_id: int, db: AsyncSession = Depends(get_database)):
    repo = CasaRepository(db)
    casa = await repo.get_by_id(casa_id)
    if not casa:
        raise HTTPException(status_code=404, detail="Casa não encontrada")
    return casa

@router.post("", response_model=CasaResponse, status_code=status.HTTP_201_CREATED)
async def create_casa(casa: CasaCreate, db: AsyncSession = Depends(get_database)):
    repo = CasaRepository(db)
    new_casa = await repo.create(casa.dict())
    return new_casa

@router.put("/{casa_id}", response_model=CasaResponse)
async def update_casa(casa_id: int, casa_update: CasaUpdate, db: AsyncSession = Depends(get_database)):
    repo = CasaRepository(db)
    updated = await repo.update(casa_id, casa_update.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Casa não encontrada")
    return updated

@router.delete("/{casa_id}")
async def delete_casa(casa_id: int, db: AsyncSession = Depends(get_database)):
    repo = CasaRepository(db)
    deleted = await repo.delete(casa_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Casa não encontrada")
    return {"message": "Casa deletada com sucesso"}
