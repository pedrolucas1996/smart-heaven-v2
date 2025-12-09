"""Events controller - REST API for event injection and mapping management."""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db import get_session
from src.repositories.mapping_repo import MappingRepository
from src.repositories.lamp_repo import LampRepository
from src.repositories.light_repo import LightRepository
from src.services.mqtt_service import mqtt_service
from src.services.event_service import EventService
from src.services.event_cache import EventCache
from src.namespaces.events.schemas import (
    EventPayload,
    MappingBase,
    MappingCreate,
    MappingUpdate,
    MappingResponse
)

router = APIRouter(prefix="/api/v1/events", tags=["events"])

# Initialize event cache (singleton)
event_cache = EventCache(ttl_seconds=5)


async def get_event_service(
    session: AsyncSession = Depends(get_session)
) -> EventService:
    """Dependency to get EventService instance."""
    mapping_repo = MappingRepository(session)
    lamp_repo = LampRepository(session)
    light_repo = LightRepository(session)
    
    return EventService(
        mapping_repo=mapping_repo,
        lamp_repo=lamp_repo,
        light_repo=light_repo,
        mqtt_service=mqtt_service,
        event_cache=event_cache
    )


@router.post(
    "",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Inject manual event",
    description="Manually inject a button event for testing or automation triggers"
)
async def inject_event(
    event: EventPayload,
    event_service: EventService = Depends(get_event_service)
) -> Dict[str, Any]:
    """
    Inject a manual button event.
    
    This endpoint allows manual triggering of button events for:
    - Testing automation rules
    - Web interface button controls
    - Integration with external systems
    
    The event will be processed through the normal automation pipeline:
    1. Check for duplicates (5 second window)
    2. Find matching mappings
    3. Execute actions (turn on/off lamps, control groups)
    4. Publish MQTT commands
    
    Args:
        event: Button event data (device, button, action)
        event_service: Injected EventService instance
        
    Returns:
        Processing result with executed mappings and actions
        
    Example:
        ```json
        {
            "device": "ESP_BaseA",
            "button": "B1",
            "action": "press"
        }
        ```
    """
    try:
        result = await event_service.process_button_event(event)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing event: {str(e)}"
        )


@router.get(
    "/mappings",
    response_model=List[MappingResponse],
    summary="List all mappings",
    description="Get all automation mappings (active and inactive)"
)
async def list_mappings(
    session: AsyncSession = Depends(get_session)
) -> List[MappingResponse]:
    """
    List all automation mappings.
    
    Returns all configured mappings including:
    - Active mappings (currently in use)
    - Inactive mappings (disabled)
    - Wildcard mappings (device=*, button=*)
    
    Returns:
        List of all mappings with their configuration
    """
    try:
        repo = MappingRepository(session)
        mappings = await repo.get_all_mappings()
        return [MappingResponse.model_validate(m) for m in mappings]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching mappings: {str(e)}"
        )


@router.get(
    "/mappings/{mapping_id}",
    response_model=MappingResponse,
    summary="Get mapping by ID",
    description="Get a specific mapping by its ID"
)
async def get_mapping(
    mapping_id: int,
    session: AsyncSession = Depends(get_session)
) -> MappingResponse:
    """
    Get a specific mapping by ID.
    
    Args:
        mapping_id: Mapping ID
        session: Database session
        
    Returns:
        Mapping details
        
    Raises:
        404: Mapping not found
    """
    try:
        repo = MappingRepository(session)
        mapping = await repo.get_by_id(mapping_id)
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mapping {mapping_id} not found"
            )
        
        return MappingResponse.model_validate(mapping)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching mapping: {str(e)}"
        )


@router.post(
    "/mappings",
    response_model=MappingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new mapping",
    description="Create a new automation mapping"
)
async def create_mapping(
    mapping: MappingCreate,
    session: AsyncSession = Depends(get_session)
) -> MappingResponse:
    """
    Create a new automation mapping.
    
    Defines a rule that triggers actions when a button event occurs.
    
    Args:
        mapping: Mapping data
        session: Database session
        
    Returns:
        Created mapping
        
    Example:
        ```json
        {
            "device": "ESP_BaseA",
            "button": "B1",
            "action": "press",
            "target_type": "lampada_on",
            "target_value": "L_Sala",
            "priority": 100,
            "ativo": true
        }
        ```
    """
    try:
        repo = MappingRepository(session)
        new_mapping = await repo.create_mapping(mapping)
        return MappingResponse.model_validate(new_mapping)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating mapping: {str(e)}"
        )


@router.put(
    "/mappings/{mapping_id}",
    response_model=MappingResponse,
    summary="Update mapping",
    description="Update an existing mapping"
)
async def update_mapping(
    mapping_id: int,
    mapping: MappingUpdate,
    session: AsyncSession = Depends(get_session)
) -> MappingResponse:
    """
    Update an existing mapping.
    
    All fields are optional - only provided fields will be updated.
    
    Args:
        mapping_id: Mapping ID to update
        mapping: Updated mapping data
        session: Database session
        
    Returns:
        Updated mapping
        
    Raises:
        404: Mapping not found
    """
    try:
        repo = MappingRepository(session)
        
        # Check if exists
        existing = await repo.get_by_id(mapping_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mapping {mapping_id} not found"
            )
        
        # Update
        updated = await repo.update_mapping(mapping_id, mapping)
        return MappingResponse.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating mapping: {str(e)}"
        )


@router.delete(
    "/mappings/{mapping_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete mapping",
    description="Delete a mapping"
)
async def delete_mapping(
    mapping_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a mapping.
    
    Args:
        mapping_id: Mapping ID to delete
        session: Database session
        
    Raises:
        404: Mapping not found
    """
    try:
        repo = MappingRepository(session)
        
        # Check if exists
        existing = await repo.get_by_id(mapping_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mapping {mapping_id} not found"
            )
        
        # Delete
        await repo.delete_mapping(mapping_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting mapping: {str(e)}"
        )


@router.post(
    "/mappings/{mapping_id}/activate",
    response_model=MappingResponse,
    summary="Activate mapping",
    description="Enable a mapping"
)
async def activate_mapping(
    mapping_id: int,
    session: AsyncSession = Depends(get_session)
) -> MappingResponse:
    """
    Activate (enable) a mapping.
    
    Args:
        mapping_id: Mapping ID to activate
        session: Database session
        
    Returns:
        Updated mapping
        
    Raises:
        404: Mapping not found
    """
    try:
        repo = MappingRepository(session)
        
        # Check if exists
        existing = await repo.get_by_id(mapping_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mapping {mapping_id} not found"
            )
        
        # Activate
        updated = await repo.activate_mapping(mapping_id)
        return MappingResponse.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating mapping: {str(e)}"
        )


@router.post(
    "/mappings/{mapping_id}/deactivate",
    response_model=MappingResponse,
    summary="Deactivate mapping",
    description="Disable a mapping"
)
async def deactivate_mapping(
    mapping_id: int,
    session: AsyncSession = Depends(get_session)
) -> MappingResponse:
    """
    Deactivate (disable) a mapping.
    
    Args:
        mapping_id: Mapping ID to deactivate
        session: Database session
        
    Returns:
        Updated mapping
        
    Raises:
        404: Mapping not found
    """
    try:
        repo = MappingRepository(session)
        
        # Check if exists
        existing = await repo.get_by_id(mapping_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mapping {mapping_id} not found"
            )
        
        # Deactivate
        updated = await repo.deactivate_mapping(mapping_id)
        return MappingResponse.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating mapping: {str(e)}"
        )


@router.get(
    "/cache/stats",
    response_model=Dict[str, Any],
    summary="Get cache statistics",
    description="Get event cache statistics (for debugging)"
)
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get event cache statistics.
    
    Returns information about:
    - Current cache size
    - TTL configuration
    - Hit/miss tracking (if implemented)
    
    Returns:
        Cache statistics
    """
    return event_cache.get_stats()
