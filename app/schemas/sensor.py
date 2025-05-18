from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

from app.core.config import settings

class SensorDataCreate(BaseModel):
    """Schema for incoming sensor data"""
    device_id: str = Field(..., description="Unique identifier for the device", max_length=50)
    temperature: float = Field(..., description="Temperature reading in Celsius")
    humidity: float = Field(..., description="Humidity reading in percentage")
    timestamp: datetime = Field(..., description="Timestamp of the reading")
    
    @field_validator("temperature")
    def validate_temperature(cls, v):
        if v < settings.MIN_TEMPERATURE or v > settings.MAX_TEMPERATURE:
            raise ValueError(f"Temperature must be between {settings.MIN_TEMPERATURE}°C and {settings.MAX_TEMPERATURE}°C")
        return v
    
    @field_validator("humidity")
    def validate_humidity(cls, v):
        if v < settings.MIN_HUMIDITY or v > settings.MAX_HUMIDITY:
            raise ValueError(f"Humidity must be between {settings.MIN_HUMIDITY}% and {settings.MAX_HUMIDITY}%")
        return v    


class SensorDataResponse(BaseModel):
    """Schema for sensor data response"""
    id: int
    device_id: str
    temperature: float
    humidity: float
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SensorDataIngestionResponse(BaseModel):
    """Response for successful data ingestion"""
    message: str = "Data received and being processed"
    request_id: UUID = Field(default_factory=uuid4)

class DeviceReadingsResponse(BaseModel):
    """Response for device readings"""
    device_id: str
    readings: List[SensorDataResponse]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = settings.APP_VERSION
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    