import logging
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud import create_sensor_data, get_device_readings
from app.database.models import get_session
from app.schemas.sensor import (
    SensorDataCreate,
    SensorDataResponse,
    SensorDataIngestionResponse,
    DeviceReadingsResponse,
)
from app.core.config import settings

# Create router
router = APIRouter(prefix="/sensors", tags=["sensors"])

# Configure logging
logger = logging.getLogger(__name__)

async def process_sensor_data(data: SensorDataCreate, db: AsyncSession) -> None:
    """Background task to process and store sensor data"""
    try:
        # Log the incoming data
        logger.info(f"Processing data for device: {data.device_id}")
        # Store the data in the database
        await create_sensor_data(db=db, data=data)
        # Commit the transaction
        await db.commit()
        logger.info(f"Data for device {data.device_id} processed successfully")
    except Exception as e:
        # Rollback in case of error
        await db.rollback()
        logger.error(f"Error processing data for device {data.device_id}: {str(e)}")
    finally:
        # Ensure connection is closed/returned to pool
        await db.close()


@router.post(
    "/data",
    response_model=SensorDataIngestionResponse,
    status_code=202,
    summary="Submit sensor data",
    description="Submit sensor data for ingestion. The data will be processed asynchronously.",
)
async def ingest_sensor_data(
    data: SensorDataCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
) -> SensorDataIngestionResponse:
    """
    Ingest sensor data and process it asynchronously
    """
    # Queue the data processing task
    background_tasks.add_task(process_sensor_data, data=data, db=db)
    
    # Return immediately with a 202 Accepted response
    return SensorDataIngestionResponse()

@router.get(
    "/data/{device_id}",
    response_model=DeviceReadingsResponse,
    status_code=202,
    summary="Get device readings",
    description="Get the latest readings for a specific device.",
)
async def get_device_data(
    device_id: str,
    limit: int = Query(
        default=settings.DEFAULT_LIMIT,
        le=settings.MAX_LIMIT,
        gt=1,
        description="Maximum number of readings to return",
    ),
    db: AsyncSession = Depends(get_session),
) -> DeviceReadingsResponse:
    """
    Get the latest readings for a specific device
    """
    # Fetch device readings
    readings = await get_device_readings(db=db, device_id=device_id, limit=limit)
    
    # If no readings found, return an empty list
    if not readings:
        return DeviceReadingsResponse(device_id=device_id, readings=[])
    
    # Convert SQLAlchemy models to Pydantic models
    response_readings = [
        SensorDataResponse(
            id=reading.id,
            device_id=reading.device_id,
            temperature=reading.temperature,
            humidity=reading.humidity,
            timestamp=reading.timestamp,
        )
        for reading in readings
    ]
    
    return DeviceReadingsResponse(device_id=device_id, readings=response_readings)