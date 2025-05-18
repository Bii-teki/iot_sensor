import os
from datetime import datetime
from typing import List
from pydantic import BaseModel

class Settings(BaseModel):
    # API settings
    APP_NAME: str = "IoT Sensor Data Ingestion API"
    APP_DESCRIPTION: str = "A FastAPI service for ingesting and retrieving IoT sensor data"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./sensor_data.db"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Validation settings
    MIN_TEMPERATURE: float = -50.0
    MAX_TEMPERATURE: float = 150.0
    MIN_HUMIDITY: float = 0.0
    MAX_HUMIDITY: float = 100.0
    
    # Pagination defaults
    DEFAULT_LIMIT: int = 10
    MAX_LIMIT: int = 100

# Load environment variables
settings = Settings()

# Override settings from environment variables
for field in settings.model_fields:
    env_value = os.getenv(field.upper())
    if env_value:
        setattr(settings, field, env_value)