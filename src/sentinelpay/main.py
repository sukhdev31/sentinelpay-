from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from sentinelpay.api.routes.analytics import router as analytics_router
from sentinelpay.api.routes.cases import router as cases_router
from sentinelpay.api.routes.health import router as health_router
from sentinelpay.api.routes.operations import router as operations_router
from sentinelpay.api.routes.scoring import router as scoring_router
from sentinelpay.core.cache import close_cache
from sentinelpay.core.config import get_settings
from sentinelpay.core.database import close_database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await close_cache()
    await close_database()


def create_app() -> FastAPI:
    """Create and configure the SentinelPay API application."""

    settings = get_settings()
    application = FastAPI(
        title="SentinelPay Fraud Intelligence API",
        summary="Real-time payment fraud scoring and decisioning platform.",
        description=(
            "SentinelPay combines policy rules, machine learning, anomaly "
            "detection, and graph-risk signals to evaluate transactions."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    application.include_router(
        health_router,
        prefix="/api/v1",
    )
    application.include_router(
        scoring_router,
        prefix="/api/v1",
    )
    application.include_router(cases_router, prefix="/api/v1")
    application.include_router(analytics_router, prefix="/api/v1")
    application.include_router(operations_router)

    @application.get("/", include_in_schema=False)
    async def dashboard() -> FileResponse:
        path = Path(__file__).with_name("static") / "dashboard.html"
        return FileResponse(path)

    return application


app = create_app()
