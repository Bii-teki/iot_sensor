from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import SensorData
from app.schemas.sensor import SensorDataCreate, SensorDataResponse

async def create_sensor_data(db: AsyncSession, data: SensorDataCreate) -> SensorData:
    """Create a new sensor data record"""
    db_data = SensorData(
        device_id=data.device_id,
        temperature=data.temperature,
        humidity=data.humidity,
        timestamp=data.timestamp,
    )
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data

async def get_device_readings(
    db: AsyncSession, device_id: str, limit: int
) -> List[SensorData]:
    """Get the latest readings for a specific device"""
    query = (
        select(SensorData)
        .where(SensorData.device_id == device_id)
        .order_by(SensorData.timestamp.desc())
        .limit(limit)
    )
    if limit > 0:
        query = query.limit(limit)

    result = await db.execute(query)
    return result.scalars().all()

async def count_sensor_data() -> int:
    """Count the total number of sensor data records"""
    async with AsyncSession() as session:
        result = await session.execute(select(func.count(SensorData.id)))
        return result.scalar() or 0