from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    ForeignKey, Enum, Index, Text
)
from sqlalchemy.orm import relationship
from src.infra.db import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)

    base_id = Column(
        Integer,
        ForeignKey("base_hardware.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Identidade física
    gpio = Column(Integer, nullable=False)
    gpio_index = Column(Integer, nullable=False, default=1)

    # Comportamento
    direction = Column(
        Enum("input", "output", name="device_direction_enum"),
        nullable=False
    )

    function = Column(
        Enum(
            "lamp", "button", "relay", "pir", "sensor",
            "gate", "generic",
            name="device_function_enum"
        ),
        default="generic",
        nullable=False
    )

    data_type = Column(
        Enum(
            "boolean", "integer", "float", "string",
            name="device_data_type_enum"
        ),
        nullable=True
    )

    unit = Column(String(20), nullable=True)
    sampling_interval = Column(Integer, nullable=True)

    invert_logic = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)

    # UX / Frontend (não vai para o ESP)
    alias = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Relacionamento
    base = relationship("HardwareBase", back_populates="devices")

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        Index(
            "idx_unique_gpio",
            "base_id", "gpio", "gpio_index",
            unique=True
        ),
    )

    def __repr__(self):
        return (
            f"<Device GPIO[{self.gpio}][{self.gpio_index}] "
            f"{self.direction}/{self.function}>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "base_id": self.base_id,
            "gpio": self.gpio,
            "gpio_index": self.gpio_index,
            "direction": self.direction,
            "function": self.function,
            "data_type": self.data_type,
            "unit": self.unit,
            "sampling_interval": self.sampling_interval,
            "invert_logic": self.invert_logic,
            "enabled": self.enabled,
            "alias": self.alias,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
