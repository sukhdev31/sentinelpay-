import hmac
from typing import Annotated

from fastapi import Header, HTTPException, status

from sentinelpay.core.config import get_settings


async def require_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    """Require a constant-time API-key match on protected routes."""

    settings = get_settings()
    if not settings.api_key_required:
        return

    expected = settings.api_key.get_secret_value()
    if x_api_key is None or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-API-Key header is required",
        )
