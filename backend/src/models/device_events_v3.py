from datetime import datetime
from sqlalchemy import (
    Column, Integer, DateTime, Boolean, ForeignKey,
    Enum, JSON, Index
)
from src.infra.db import Base


class DeviceEvent(Base):
    __tablename__ = "device_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identidade (redundância intencional)
    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    base_id = Column(Integer, nullable=False, index=True)
    id_house = Column(Integer, nullable=False, index=True)

    # Evento
    event_type = Column(
        Enum(
            "state_change",
            "button_press",
            "command_sent",
            "boot",
            "heartbeat",
            "error",
            name="device_event_type_enum"
        ),
        nullable=False
    )

    state = Column(Boolean, nullable=True)

    action = Column(String(50), nullable=True)
    # ex: "toggle", "on", "off", "press", "long_press"

    # Contexto
    origin = Column(
        Enum(
            "button", "web", "mqtt", "automation", "system", "device",
            name="device_event_origin_enum"
        ),
        nullable=False
    )

    rssi = Column(Integer, nullable=True)

    payload = Column(JSON, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<DeviceEvent type={self.event_type} "
            f"device={self.device_id} "
            f"origin={self.origin}>"
        )
