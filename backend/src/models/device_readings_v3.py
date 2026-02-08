from datetime import datetime
from sqlalchemy import (
    Column, Integer, DateTime, Float, ForeignKey, Index
)
from src.infra.db import Base


class DeviceReading(Base):
    __tablename__ = "device_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    value = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_device_reading_time", "device_id", "created_at"),
    )
    def __repr__(self):
        return (
            f"<DeviceReading device={self.device_id} "
            f"value={self.value} "
            f"created_at={self.created_at}>"
        )