from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from sentinelpay.main import app

client = TestClient(app)


async def dependency_ready() -> bool:
    return True


async def dependency_unavailable() -> bool:
    return False


def test_health_endpoint_returns_service_status() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["service"] == "sentinelpay-api"
    assert payload["version"] == "1.0.0"
    assert datetime.fromisoformat(payload["timestamp"])


def test_openapi_document_is_available() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == ("SentinelPay Fraud Intelligence API")


def test_readiness_returns_ready_when_dependencies_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sentinelpay.api.routes.health.database_is_ready",
        dependency_ready,
    )
    monkeypatch.setattr(
        "sentinelpay.api.routes.health.cache_is_ready",
        dependency_ready,
    )

    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["services"] == {
        "api": "ready",
        "postgres": "ready",
        "redis": "ready",
    }


def test_readiness_returns_503_when_dependency_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sentinelpay.api.routes.health.database_is_ready",
        dependency_unavailable,
    )
    monkeypatch.setattr(
        "sentinelpay.api.routes.health.cache_is_ready",
        dependency_ready,
    )

    response = client.get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["services"]["postgres"] == "unavailable"
