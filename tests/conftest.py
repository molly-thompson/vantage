from typing import Any

import pytest

from accounts.models import User
from systems.models import ApiEntity, System


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


@pytest.fixture
def system(user: User) -> System:
    return System.objects.create(
        name="Test System",
        owner=user,
    )


@pytest.fixture
def api_entity(system: System) -> ApiEntity:
    return ApiEntity.objects.create(
        system=system,
        name="TestAPI",
        key_hash="test-key-hash",
    )
