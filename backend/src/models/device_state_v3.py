from datetime import datetime
from sqlalchemy import (
    Column, Integer, DateTime, Boolean,
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from src.infra.db import Base


class DeviceState(Base):
    __tablename__ = "device_state"

    id = Column(Integer, primary_key=True, autoincrement=True)

    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Estado atual
    state = Column(Boolean, nullable=False)

    # Contexto
    origin = Column(
        Enum(
            "button", "web", "mqtt", "automation", "system",
            name="device_state_origin_enum"
        ),
        nullable=False
    )

    rssi = Column(Integer, nullable=True)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    device = relationship("Device")

    __table_args__ = (
        UniqueConstraint("device_id", name="uq_device_state_device"),
    )

    def __repr__(self):
        return f"<DeviceState device={self.device_id} state={self.state}>"

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "state": self.state,
            "origin": self.origin,
            "rssi": self.rssi,
            "updated_at": self.updated_at.isoformat(),
        }
