"""Switch management controller."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.deps import get_database
from src.namespaces.switches.schemas import (
    SwitchResponse,
    SwitchCreate,
    SwitchUpdate,
    SwitchCommand,
)
from src.namespaces.system.schemas import MessageResponse
from src.services.switch_service import SwitchService

router = APIRouter(prefix="/switches", tags=["Switches"])


@router.get("", response_model=List[SwitchResponse])
async def get_all_switches(db: AsyncSession = Depends(get_database)):
    """
    Get all switches in the system.
    
    Returns a list of all registered switches with their states.
    """
    service = SwitchService(db)
    switches = await service.get_all_switches()
    return switches


@router.get("/{nome}", response_model=SwitchResponse)
async def get_switch(
    nome: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Get a specific switch by name.
    
    - **nome**: Switch name/identifier
    """
    service = SwitchService(db)
    switch = await service.get_switch_by_name(nome)
    
    if not switch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Switch '{nome}' not found"
        )
    
    return switch


@router.post("", response_model=SwitchResponse, status_code=status.HTTP_201_CREATED)
async def create_switch(
    switch_data: SwitchCreate,
    db: AsyncSession = Depends(get_database)
):
    """
    Create a new switch.
    
    - **nome**: Switch name
    - **base**: Base/board name
    - **ativo**: Enabled state (default: true)
    """
    service = SwitchService(db)
    
    # Check if switch already exists
    existing = await service.get_switch_by_name(switch_data.nome)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Switch '{switch_data.nome}' already exists"
        )
    
    from src.repositories.switch_repo import SwitchRepository
    repo = SwitchRepository(db)
    switch = await repo.create({
        "nome": switch_data.nome,
        "base": switch_data.base,
        "estado": False,
        "ativo": switch_data.ativo
    })
    await db.commit()
    
    return switch


@router.patch("/{nome}", response_model=SwitchResponse)
async def update_switch(
    nome: str,
    switch_data: SwitchUpdate,
    db: AsyncSession = Depends(get_database)
):
    """
    Update a switch's state.
    
    - **nome**: Switch identifier
    - **ativo**: Enable/disable switch
    - **estado**: Physical button state
    """
    service = SwitchService(db)
    switch = await service.get_switch_by_name(nome)
    
    if not switch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Switch '{nome}' not found"
        )
    
    from src.repositories.switch_repo import SwitchRepository
    repo = SwitchRepository(db)
    
    if switch_data.ativo is not None:
        switch = await repo.update_active_state(nome, switch_data.ativo)
    
    if switch_data.estado is not None:
        switch = await repo.update_physical_state(nome, switch_data.estado)
    
    await db.commit()
    
    return switch


@router.post("/control", response_model=MessageResponse)
async def control_switch(
    command: SwitchCommand,
    db: AsyncSession = Depends(get_database)
):
    """
    Enable or disable a switch.
    
    - **botao**: Switch name
    - **acao**: Action to perform ("habilitar" or "desabilitar")
    """
    service = SwitchService(db)
    
    if command.acao == "habilitar":
        result = await service.enable_switch(command.botao)
    else:
        result = await service.disable_switch(command.botao)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post("/{nome}/enable", response_model=MessageResponse)
async def enable_switch(
    nome: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Enable a switch.
    
    - **nome**: Switch identifier
    """
    service = SwitchService(db)
    result = await service.enable_switch(nome)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post("/{nome}/disable", response_model=MessageResponse)
async def disable_switch(
    nome: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Disable a switch.
    
    - **nome**: Switch identifier
    """
    service = SwitchService(db)
    result = await service.disable_switch(nome)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return MessageResponse(
        message=result["message"],
        success=True
    )
