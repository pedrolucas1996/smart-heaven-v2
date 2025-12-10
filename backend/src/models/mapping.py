"""Mapping model for event-to-action mappings.

Maps device events (button presses) to actions (light toggles, scenes, etc).
Enables flexible automation rules without changing firmware.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.dialects.mysql import JSON

from src.infra.db import Base


class Mapping(Base):
    """
    Event-to-action mapping table.
    
    Maps source events (device + button + action) to target actions.
    Multiple mappings can exist for the same source event (trigger multiple actions).
    
    Examples:
        - Base_D + S1 + press -> toggle L_Cozinha
        - Base_A + S2 + press -> scene "Movie Mode"
        - Base_Portao + S1 + press -> pulse_sequence gate
    """
    __tablename__ = "mappings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
        
    id_house = Column(Integer, nullable=False)
    # Source event identification
    source_device = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Source device identifier (e.g., Base_D, Base_A)"
    )
    source_button = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Button identifier (e.g., S1, S2, *=wildcard)"
    )
    source_action = Column(
        String(20),
        nullable=True,
        default="press",
        comment="Button action filter (press, release, changed, *=any)"
    )
    
    # Target action
    action_type = Column(
        String(50),
        nullable=False,
        comment="Action to perform: toggle_light, turn_on, turn_off, scene, script, pulse_gate"
    )
    target_type = Column(
        String(50),
        nullable=False,
        comment="Target type: light, gate, scene, script, notification"
    )
    target_id = Column(
        String(100),
        nullable=False,
        comment="Target identifier (comodo name, scene id, script path)"
    )
    
    # Additional parameters (JSON)
    parameters_json = Column(
        JSON,
        nullable=True,
        comment="Additional parameters for the action (e.g., pulse count, delay)"
    )
    
    # Control fields
    active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether this mapping is active"
    )
    priority = Column(
        Integer,
        nullable=False,
        default=100,
        comment="Execution priority (lower = higher priority)"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description of what this mapping does"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When mapping was created"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="When mapping was last updated"
    )
    
    def __repr__(self):
        return (
            f"<Mapping(id={self.id}, "
            f"{self.source_device}.{self.source_button} -> "
            f"{self.action_type} {self.target_type}:{self.target_id})>"
        )
    
    def matches_event(self, device: str, button: str, action: str) -> bool:
        """
        Check if this mapping matches the given event.
        
        Supports wildcards:
        - source_button='*' matches any button
        - source_action='*' or None matches any action
        
        Args:
            device: Source device identifier
            button: Button identifier
            action: Button action (press, release, changed)
            
        Returns:
            True if mapping matches event
        """
        if not self.active:
            return False
        
        # Device must match exactly
        if self.source_device != device:
            return False
        
        # Button can be wildcard
        if self.source_button != "*" and self.source_button != button:
            return False
        
        # Action can be wildcard or None (matches any)
        if self.source_action and self.source_action != "*" and self.source_action != action:
            return False
        
        return True
