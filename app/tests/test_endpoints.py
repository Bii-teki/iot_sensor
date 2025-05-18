import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import delete
from app.database.models import SensorData
from app.database.crud import create_sensor_data
from app.schemas.sensor import SensorDataCreate

@pytest.mark.asyncio
async def test_health_endpoint(test_client: TestClient):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data

@pytest.mark.asyncio
async def test_ingest_sensor_data(test_client: TestClient, sample_sensor_data: SensorDataCreate):
    payload = sample_sensor_data.model_dump()
    payload["timestamp"] = payload["timestamp"].isoformat()
    
    response = test_client.post("/api/sensors/data", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["message"] == "Data received and being processed"
    assert "request_id" in data

@pytest.mark.asyncio
async def test_get_device_data_empty(test_client: TestClient):
    response = test_client.get("/api/sensors/data/nonexistent-device")
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "nonexistent-device"
    assert data["readings"] == []

@pytest.mark.asyncio
async def test_get_device_data(test_client, db_session):
    device_id = "test-device-002"
    now = datetime.utcnow() - timedelta(minutes=10)

    async for session in db_session:
                # First, clear any existing data for this device
        await session.execute(delete(SensorData))
        await session.commit()
        for i in range(3):
            data = SensorDataCreate(
                device_id=device_id,
                temperature=20.0 + i,
                humidity=50.0 + i,
                timestamp=now - timedelta(minutes=i * 5)
            )
            await create_sensor_data(session, data)

        # Perform the GET request
        response = test_client.get(f"/api/sensors/data/{device_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["device_id"] == device_id
        # assert len(data["readings"]) == 3

        timestamps = [reading["timestamp"] for reading in data["readings"]]
        assert timestamps == sorted(timestamps, reverse=True)

        break

@pytest.mark.asyncio
async def test_get_device_data_with_limit(test_client, db_session):
    device_id = "test-device-003"
    now = datetime.utcnow() - timedelta(minutes=10)

    async for session in db_session:
        await session.execute(delete(SensorData).where(SensorData.device_id == device_id))
        await session.commit()
        for i in range(3):
            data = SensorDataCreate(
                device_id=device_id,
                temperature=20.0 + i,
                humidity=50.0 + i,
                timestamp=now - timedelta(minutes=i * 5)
            )
            await create_sensor_data(session, data)

        # Make request after inserting data
        response = test_client.get(f"/api/sensors/data/{device_id}?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == device_id
        assert len(data["readings"]) == 2
        break

@pytest.mark.asyncio
async def test_invalid_temperature(test_client: TestClient):
    payload = {
        "device_id": "test-device-004",
        "temperature": 200.0,
        "humidity": 60.0,
        "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    }
    
    response = test_client.post("/api/sensors/data", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "temperature" in str(data["detail"])

@pytest.mark.asyncio
async def test_invalid_humidity(test_client: TestClient):
    payload = {
        "device_id": "test-device-005",
        "temperature": 25.0,
        "humidity": 120.0,
        "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    }
    
    response = test_client.post("/api/sensors/data", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "humidity" in str(data["detail"])
