from datetime import datetime
from sqlalchemy import (
    Column, Integer, DateTime, Boolean,
    ForeignKey, Enum, String, Index
)
from src.infra.db import Base


class DeviceLink(Base):
    __tablename__ = "device_links"

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_house = Column(Integer, nullable=False, index=True)

    # Origem
    source_device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    source_event = Column(
        Enum(
            "press",
            "release",
            "long_press",
            "state_change",
            name="device_link_source_event_enum"
        ),
        nullable=False
    )

    # Destino
    target_device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    target_action = Column(
        Enum(
            "toggle",
            "on",
            "off",
            "pulse",
            name="device_link_target_action_enum"
        ),
        nullable=False
    )

    # Controle
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return (
            f"<DeviceLink {self.source_device_id} "
            f"{self.source_event} -> "
            f"{self.target_device_id} "
            f"{self.target_action}>"
        )
