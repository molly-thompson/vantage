import pytest

from accounts.models import User
from logs.helpers import get_sentinel_user


@pytest.mark.django_db
def test_get_sentinel_user_creates_sentinel() -> None:
    sentinel = get_sentinel_user()

    assert sentinel.email == "deleted@vantage.invalid"
    assert sentinel.first_name == "Deleted"
    assert sentinel.last_name == "User"


@pytest.mark.django_db
def test_get_sentinel_user_returns_existing_sentinel() -> None:
    existing_sentinel = User.objects.create(
        email="deleted@vantage.invalid",
        first_name="Deleted",
        last_name="User",
    )

    sentinel = get_sentinel_user()

    assert sentinel == existing_sentinel
    assert User.objects.filter(email="deleted@vantage.invalid").count() == 1


@pytest.mark.django_db
def test_get_sentinel_user_returns_user_with_expected_display_name() -> None:
    sentinel = get_sentinel_user()

    assert str(sentinel) == "Deleted User"
