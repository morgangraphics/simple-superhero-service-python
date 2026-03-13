"""
Simple Health check route
"""

from fastapi import APIRouter

from ..models import HealthResponse

bp_hc = APIRouter()


@bp_hc.get("/healthcheck", tags=["healthcheck"], summary="Test if the Service is up", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    """Simple health check endpoint."""
    return HealthResponse(status="Ok")

