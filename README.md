# IoT Sensor Data Ingestion API

A FastAPI-based service for real-time IoT sensor data ingestion and retrieval, featuring asynchronous processing and robust data validation.

## Features

- ⚡️ Real-time data ingestion with background processing
- 🔒 Built-in data validation and range verification
- 📊 Device-specific data retrieval with pagination
- 🗄️ SQLite database with async support
- 🔍 Health monitoring endpoint
- 🐳 Docker support for easy deployment
- ✅ Comprehensive test suite

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: SQLite (via SQLAlchemy)
- **Testing**: pytest
- **Containerization**: Docker
- **API Documentation**: Swagger/OpenAPI

## Quick Start

### Using Docker (Recommended)

```bash
# Build and start the container
docker-compose up --build
```

The API will be available at http://localhost:8000

### Manual Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  
```
or 
```bash
pipenv install && pipenv shell
```

2. Install dependencies:
cd app
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Submit Sensor Data
```http
POST /api/sensors/data
```
```json
{
  "device_id": "sensor-001",
  "temperature": 23.5,
  "humidity": 65.0,
  "timestamp": "2025-05-17T10:00:00Z"
}
```

#### Get Device Readings
```http
GET /api/sensors/data/{device_id}?limit=10
```

#### Health Check
```http
GET /health
```

## Data Validation

- Temperature: -50°C to 150°C
- Humidity: 0% to 100%
- Device ID: Max 50 characters
- Timestamp: ISO 8601 format

## Development

### Project Structure
```
app/
├── core/           # Core configuration
├── database/       # Database models and operations
├── models/         # Pydantic models
├── schemas/         # Data validation
├── routes/         # API endpoints
└── tests/          # Test suite

```

### Running Tests

```bash
pytest
```

### Simulating Sensor Data

You can simulate sensor data in two ways:

1. From the app directory:
```bash
cd app
python3 data_simulator.py
```

Simulator will generate realistic sensor data from multiple virtual devices and send it to your API. This is useful for testing and development purposes.
## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | IoT Sensor Data Ingestion API |
| DATABASE_URL | Database connection URL | sqlite+aiosqlite:///./sensor_data.db |
| MIN_TEMPERATURE | Minimum allowed temperature | -50.0 |
| MAX_TEMPERATURE | Maximum allowed temperature | 150.0 |
| MIN_HUMIDITY | Minimum allowed humidity | 0.0 |
| MAX_HUMIDITY | Maximum allowed humidity | 100.0 |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for the robust ORM
- The Python community for amazing async support