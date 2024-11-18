from fastapi import APIRouter

from .dtos import HealthCheckResponse

_TAG = "Health"

router = APIRouter(tags=[_TAG])


@router.get("/health")
def get_api_health() -> HealthCheckResponse:
    return HealthCheckResponse(status="ok")
