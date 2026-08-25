from django.conf import settings


def test_example() -> None:
    assert True


def test_django_settings() -> None:
    assert settings.configured
