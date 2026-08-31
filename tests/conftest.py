from typing import Any

import pytest

from accounts.models import User


@pytest.fixture(autouse=True)
def disable_ssl_redirect(settings: Any) -> None:
    settings.SECURE_SSL_REDIRECT = False


@pytest.fixture
def user() -> User:
    return User.objects.create_user(
        username="testuser",
        email="user@example.com",
        password="password123",
    )
