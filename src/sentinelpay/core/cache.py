from redis.asyncio import Redis

from sentinelpay.core.config import get_settings

settings = get_settings()

redis_client: Redis = Redis.from_url(
    settings.redis_url.get_secret_value(),
    decode_responses=True,
    health_check_interval=30,
)


async def cache_is_ready() -> bool:
    """Return whether Redis accepts a ping command."""

    try:
        response = await redis_client.ping()
    except Exception:
        return False

    return bool(response)


async def close_cache() -> None:
    """Close the Redis connection pool."""

    await redis_client.aclose()
