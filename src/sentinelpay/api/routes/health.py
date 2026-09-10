from asyncio import gather
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from sentinelpay.core.cache import cache_is_ready
from sentinelpay.core.config import get_settings
from sentinelpay.core.database import database_is_ready

ServiceStatus = Literal["ready", "unavailable"]


class HealthResponse(BaseModel):
    """Response returned when the SentinelPay API process is alive."""

    status: Literal["healthy"] = "healthy"
    service: str = "sentinelpay-api"
    version: str = "1.0.0"
    timestamp: datetime = Field(description="Current server time represented in UTC.")


class ReadinessResponse(BaseModel):
    """Availability status for SentinelPay and its dependencies."""

    status: Literal["ready", "degraded"]
    services: dict[str, ServiceStatus]
    timestamp: datetime


router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API liveness",
)
async def health_check() -> HealthResponse:
    """Confirm that the API process is running."""

    settings = get_settings()
    return HealthResponse(version=settings.app_version, timestamp=datetime.now(UTC))


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Check service readiness",
)
async def readiness_check(response: Response) -> ReadinessResponse:
    """Check whether PostgreSQL and Redis can accept requests."""

    database_ready, redis_ready = await gather(
        database_is_ready(),
        cache_is_ready(),
    )

    services: dict[str, ServiceStatus] = {
        "api": "ready",
        "postgres": "ready" if database_ready else "unavailable",
        "redis": "ready" if redis_ready else "unavailable",
    }

    is_ready = database_ready and redis_ready

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if is_ready else "degraded",
        services=services,
        timestamp=datetime.now(UTC),
    )
