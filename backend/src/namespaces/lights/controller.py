"""Light management controller (luzes table)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.deps import get_database
from src.namespaces.lights.schemas import (
    LightResponse,
    LightCreate,
    LightUpdate,
    LightCommand,
)
from src.namespaces.system.schemas import MessageResponse
from src.services.light_service import LightService
from src.core.dependencies import get_current_active_user
from src.models.user import User

router = APIRouter(prefix="/lights", tags=["Lights"])


@router.get("", response_model=List[LightResponse])
async def get_all_lights(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all lights for the current user's house.
    
    Returns a list of all registered lights with their current states.
    """
    if not current_user.id_house:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a house"
        )
    
    service = LightService(db)
    lights = await service.get_lights_by_house(current_user.id_house)
    return lights


@router.get("/{lampada}", response_model=LightResponse)
async def get_light(
    lampada: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Get a specific light by name.
    
    - **lampada**: Light identifier/name
    """
    service = LightService(db)
    light = await service.get_light_by_name(lampada)
    
    if not light:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Light '{lampada}' not found"
        )
    
    return light


@router.post("", response_model=LightResponse, status_code=status.HTTP_201_CREATED)
async def create_light(
    light_data: LightCreate,
    db: AsyncSession = Depends(get_database)
):
    """
    Create a new light.
    
    - **lampada**: Light name/identifier
    - **estado**: Initial state (default: false)
    """
    service = LightService(db)
    
    # Check if light already exists
    existing = await service.get_light_by_name(light_data.lampada)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Light '{light_data.lampada}' already exists"
        )
    
    from src.repositories.light_repo import LightRepository
    repo = LightRepository(db)
    light = await repo.create({
        "lampada": light_data.lampada,
        "estado": light_data.estado
    })
    await db.commit()
    
    return light


@router.patch("/{lampada}", response_model=LightResponse)
async def update_light(
    lampada: str,
    light_data: LightUpdate,
    db: AsyncSession = Depends(get_database)
):
    """
    Update a light's state.
    
    - **lampada**: Light identifier
    - **estado**: New state
    """
    service = LightService(db)
    light = await service.get_light_by_name(lampada)
    
    if not light:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Light '{lampada}' not found"
        )
    
    if light_data.estado is not None:
        from src.repositories.light_repo import LightRepository
        repo = LightRepository(db)
        light = await repo.update_state(lampada, light_data.estado)
        await db.commit()
    
    return light


@router.post("/control", response_model=MessageResponse)
async def control_light(
    command: LightCommand,
    db: AsyncSession = Depends(get_database)
):
    """
    Control a light (turn on/off).
    
    - **comodo**: Light name
    - **acao**: Action to perform ("ligar" or "desligar")
    - **origem**: Command origin (default: "api")
    """
    try:
        service = LightService(db)
        
        if command.acao == "ligar":
            result = await service.turn_on_light(command.comodo, command.origem)
        else:
            result = await service.turn_off_light(command.comodo, command.origem)
        
        return MessageResponse(
            message=f"Light {command.comodo} turned {command.acao}",
            success=True
        )
    except Exception as e:
        import logging
        logging.error(f"Error controlling light: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error controlling light: {str(e)}"
        )


@router.post("/{lampada}/toggle", response_model=MessageResponse)
async def toggle_light(
    lampada: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Toggle a light's state.
    
    - **lampada**: Light identifier
    """
    service = LightService(db)
    result = await service.toggle_light(lampada, "api")
    
    return MessageResponse(
        message=f"Light {lampada} toggled to {result['acao']}",
        success=True
    )


@router.post("/{lampada}/on", response_model=MessageResponse)
async def turn_on(
    lampada: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Turn on a light.
    
    - **lampada**: Light identifier
    """
    service = LightService(db)
    await service.turn_on_light(lampada, "api")
    
    return MessageResponse(
        message=f"Light {lampada} turned on",
        success=True
    )


@router.post("/{lampada}/off", response_model=MessageResponse)
async def turn_off(
    lampada: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Turn off a light.
    
    - **lampada**: Light identifier
    """
    service = LightService(db)
    await service.turn_off_light(lampada, "api")
    
    return MessageResponse(
        message=f"Light {lampada} turned off",
        success=True
    )
