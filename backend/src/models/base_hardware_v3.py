from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from src.infra.db import Base


class HardwareBase(Base):
    __tablename__ = "base_hardware"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(50), unique=True, nullable=False, index=True)
    id_house = Column(Integer, nullable=False)

    access_level = Column(
        Enum(
            "admin", "trusted", "guest", "read_only",
            name="base_access_level_enum"
        ),
        default="admin",
        nullable=False
    )

    hardware_type = Column(String(30), nullable=False)
    mqtt_id = Column(String(50), unique=True, nullable=False, index=True)

    rssi = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)

    version_firmware = Column(String(20), nullable=True)
    version_schema = Column(Integer, default=3, nullable=False)

    status = Column(
        Enum(
            "active", "inactive", "maintenance",
            name="base_status_enum"
        ),
        default="active",
        nullable=False
    )

    last_seen = Column(DateTime, nullable=True)

    notes = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<HardwareBase {self.name} ({self.hardware_type})>"
