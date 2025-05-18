import asyncio
import aiohttp
import random
import json
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simulation configuration
NAIROBI_LOCATIONS = [
    "Westlands", "Kilimani", "Karen", "Runda", "Lavington",
    "Parklands", "South B", "Eastleigh", "Embakasi", "Ngong Road"
]

DEVICES = [
    {"id": "sensor-001"},
    {"id": "sensor-002"},
    {"id": "sensor-003"},
    {"id": "sensor-004"},
    {"id": "sensor-005"}
]

API_URL = "http://localhost:8000/api/sensors/data"
INTERVAL = 5  

async def generate_sensor_reading(device):
    """Generate a realistic sensor reading."""
    location = random.choice(NAIROBI_LOCATIONS)  
    return {
        "device_id": device["id"],
        "temperature": round(random.uniform(18.0, 28.0), 1),
        "humidity": round(random.uniform(30.0, 70.0), 1),
        "location": location,  
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

async def send_reading(session, reading):
    """Send a reading to the API."""
    try:
        async with session.post(API_URL, json=reading) as response:
            if response.status == 202:
                data = await response.json()
                logger.info(f"Sent reading for {reading['device_id']} ({reading['location']}) - Request ID: {data.get('request_id', 'N/A')}")
            else:
                logger.error(f"Failed to send reading for {reading['device_id']} ({reading['location']}): Status {response.status}")
    except Exception as e:
        logger.error(f"Error sending reading for {reading['device_id']}: {str(e)}")

async def simulate_device(session, device):
    """Continuously simulate readings for a device."""
    while True:
        reading = await generate_sensor_reading(device)
        await send_reading(session, reading)
        await asyncio.sleep(INTERVAL)

async def main():
    """Main simulation loop."""
    logger.info("Starting IoT sensor simulation...")

    async with aiohttp.ClientSession() as session:
        tasks = [simulate_device(session, device) for device in DEVICES]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
        except Exception as e:
            logger.error(f"Simulation error: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Simulation terminated by user")
