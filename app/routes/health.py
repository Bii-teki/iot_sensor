from datetime import datetime
from fastapi import APIRouter

from app.schemas.sensor import HealthResponse

# Create router
router = APIRouter(tags=["health"])

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the API.",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    """
     
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),       
    )