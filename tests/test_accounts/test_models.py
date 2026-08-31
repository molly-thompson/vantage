import pytest
from django.core.exceptions import ValidationError

from accounts.models import User


@pytest.mark.django_db
def test_user_can_be_created() -> None:
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("password123")


@pytest.mark.django_db
def test_user_email_is_unique() -> None:
    User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
    )

    duplicate = User(
        username="differentuser",
        email="test@example.com",
    )

    with pytest.raises(ValidationError):
        duplicate.full_clean()


@pytest.mark.django_db
def test_user_display_name() -> None:
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
    )

    assert str(user) == "Test User"


@pytest.mark.django_db
def test_user_display_name_with_only_first_name() -> None:
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
    )

    assert str(user) == "Test"


@pytest.mark.django_db
def test_user_display_name_with_only_last_name() -> None:
    user = User(
        username="testuser",
        email="test@example.com",
        last_name="User",
    )

    assert str(user) == "User"


@pytest.mark.django_db
def test_user_display_name_with_no_name() -> None:
    user = User(
        username="testuser",
        email="test@example.com",
    )

    assert str(user) == ""


@pytest.mark.django_db
def test_user_ordering() -> None:
    older_user = User.objects.create_user(
        username="olderuser",
        email="older@example.com",
        password="password123",
    )
    newer_user = User.objects.create_user(
        username="neweruser",
        email="newer@example.com",
        password="password123",
    )

    assert list(User.objects.all()) == [newer_user, older_user]
