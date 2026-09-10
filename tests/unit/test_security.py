import asyncio

import pytest
from fastapi import HTTPException

from sentinelpay.core.config import get_settings
from sentinelpay.core.security import require_api_key


def test_invalid_api_key_is_rejected() -> None:
    settings = get_settings()
    settings.api_key_required = True
    with pytest.raises(HTTPException) as error:
        asyncio.run(require_api_key("incorrect"))
    assert error.value.status_code == 401
