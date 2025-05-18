import os
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.database.models import Base, get_session
from app.schemas.sensor import SensorDataCreate
from sqlalchemy import delete
from app.database.models import SensorData

# Use an in-memory SQLite database for testing
# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for testing
test_engine = create_async_engine(settings.DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="function")
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)



@pytest.fixture
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            await session.execute(delete(SensorData))
            await session.commit()
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest.fixture
def test_client(db_session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_session()] = lambda: db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_sensor_data() -> SensorDataCreate:
    return SensorDataCreate(
        device_id="test-device-001",
        temperature=23.5,
        humidity=60.0,
        timestamp=datetime.utcnow() - timedelta(minutes=5)
    )
