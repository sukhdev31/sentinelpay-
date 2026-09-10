import asyncio

import pytest

from sentinelpay.core import cache as cache_module


class HealthyCache:
    closed = False

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        self.closed = True


class FailedCache:
    async def ping(self) -> bool:
        raise RuntimeError("Redis unavailable")


def test_cache_health_and_shutdown(monkeypatch: pytest.MonkeyPatch) -> None:
    healthy = HealthyCache()
    monkeypatch.setattr(cache_module, "redis_client", healthy)

    assert asyncio.run(cache_module.cache_is_ready()) is True

    asyncio.run(cache_module.close_cache())
    assert healthy.closed is True


def test_cache_failure_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cache_module, "redis_client", FailedCache())

    assert asyncio.run(cache_module.cache_is_ready()) is False
