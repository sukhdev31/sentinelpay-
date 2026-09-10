from collections.abc import Iterator

import pytest

from sentinelpay.core.config import get_settings


@pytest.fixture(autouse=True)
def disable_external_services() -> Iterator[None]:
    settings = get_settings()
    original_persistence = settings.persistence_enabled
    original_auth = settings.api_key_required
    settings.persistence_enabled = False
    settings.api_key_required = False
    yield
    settings.persistence_enabled = original_persistence
    settings.api_key_required = original_auth
