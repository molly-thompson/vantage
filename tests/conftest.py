from pathlib import Path
from typing import Any

import pytest
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from accounts.models import User
from logs.models import Log
from systems.models import ApiEntity, System


@pytest.fixture(autouse=True)
def configure_test_settings(settings: Any) -> None:
    settings.DEBUG = False
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


@pytest.fixture
def log(user: User) -> Log:
    return Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_user=user,
    )


@pytest.fixture(autouse=True)
def test_template_dir(settings: Any) -> None:
    settings.TEMPLATES[0]["DIRS"].append(
        Path(__file__).parent / "test_app_functionality"
    )


@pytest.fixture
def message_request() -> HttpRequest:
    request = RequestFactory().get("/")

    def get_response(request: HttpRequest) -> HttpResponse:
        return HttpResponse()

    SessionMiddleware(get_response).process_request(request)
    MessageMiddleware(get_response).process_request(request)

    return request
