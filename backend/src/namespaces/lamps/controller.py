"""Lamp management controller (lampada table)."""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.deps import get_database
from src.namespaces.lamps.schemas import (
    LampResponse,
    LampCreate,
    LampUpdate,
    LampCommand,
)
from src.namespaces.system.schemas import MessageResponse
from src.services.lamp_service import LampService
from src.core.dependencies import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lamps", tags=["Lamps"])


@router.get("", response_model=List[LampResponse])


async def get_all_lamps(
    db: AsyncSession = Depends(get_database),
    user = Depends(get_current_active_user)
):
    """
    Get all lamps in the system.
    
    Returns a list of all registered lamps with their current states.
    """
    service = LampService(db)
    lamps = await service.get_lamps_by_house(user.id_house)
    return lamps


@router.get("/base/{base_id}", response_model=List[LampResponse])
async def get_lamps_by_base(
    base_id: int,
    db: AsyncSession = Depends(get_database)
):
    """
    Get all lamps for a specific base.
    
    - **base_id**: Base hardware ID
    """
    service = LampService(db)
    lamps = await service.get_lamps_by_base(base_id)
    return lamps


@router.get("/{nome}", response_model=LampResponse)
async def get_lamp(
    nome: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Get a specific lamp by name.
    
    - **nome**: Lamp name/identifier
    """
    service = LampService(db)
    lamp = await service.get_lamp_by_name(nome)
    
    if not lamp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lamp '{nome}' not found"
        )
    
    return lamp


@router.post("", response_model=LampResponse, status_code=status.HTTP_201_CREATED)
async def create_lamp(
    lamp: LampCreate,
    db: AsyncSession = Depends(get_database)
):
    """
    Create a new lamp.
    
    - **nome**: Lamp name/identifier
    - **base_id**: Base hardware ID this lamp belongs to
    - **estado**: Initial state (default: False)
    """
    service = LampService(db)
    
    # Check if lamp already exists
    existing = await service.get_lamp_by_name(lamp.nome)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lamp '{lamp.nome}' already exists"
        )
    
    new_lamp = await service.create_lamp(
        nome=lamp.nome,
        base_id=lamp.base_id,
        estado=lamp.estado,
        comodo=lamp.comodo
    )
    return new_lamp


@router.put("/{lamp_id}", response_model=LampResponse)
async def update_lamp(
    lamp_id: int,
    lamp_update: LampUpdate,
    db: AsyncSession = Depends(get_database)
):
    """
    Update a lamp's properties.
    
    - **lamp_id**: Lamp ID
    - **nome**: New name (optional)
    - **base_id**: New base ID (optional)
    - **estado**: New state (optional)
    """
    service = LampService(db)
    
    update_data = lamp_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    lamp = await service.update_lamp(lamp_id, **update_data)
    
    if not lamp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lamp with ID {lamp_id} not found"
        )
    
    return lamp


@router.delete("/{lamp_id}", response_model=MessageResponse)
async def delete_lamp(
    lamp_id: int,
    db: AsyncSession = Depends(get_database)
):
    """
    Delete a lamp.
    
    - **lamp_id**: Lamp ID to delete
    """
    service = LampService(db)
    success = await service.delete_lamp(lamp_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lamp with ID {lamp_id} not found"
        )
    
    return MessageResponse(message=f"Lamp {lamp_id} deleted successfully")


@router.post("/control", response_model=dict)
async def control_lamp(
    command: LampCommand,
    db: AsyncSession = Depends(get_database)
):
    """
    Control a lamp (turn on/off).
    
    - **nome**: Lamp name
    - **acao**: Action to perform ('ligar' or 'desligar')
    - **origem**: Command origin (default: 'api')
    """
    service = LampService(db)
    
    try:
        if command.acao == "ligar":
            result = await service.turn_on_lamp(command.nome, command.origem)
        elif command.acao == "desligar":
            result = await service.turn_off_lamp(command.nome, command.origem)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {command.acao}. Use 'ligar' or 'desligar'"
            )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.error(f"Error controlling lamp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to control lamp: {str(e)}"
        )


@router.post("/{nome}/toggle", response_model=dict)
async def toggle_lamp(
    nome: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Toggle a lamp's state.
    
    - **nome**: Lamp name
    """
    service = LampService(db)
    
    try:
        result = await service.toggle_lamp(nome, "api")
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error toggling lamp {nome}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling lamp: {str(e)}"
        )
