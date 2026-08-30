from typing import Any

import pytest


@pytest.fixture(autouse=True)
def disable_ssl_redirect(settings: Any) -> None:
    settings.SECURE_SSL_REDIRECT = False
