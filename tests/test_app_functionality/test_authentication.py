import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User


def test_unauthenticated_user_is_redirected_from_protected_view(client: Client) -> None:
    response = client.get(reverse("accounts:dashboard"))

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login/")


@pytest.mark.django_db
def test_authenticated_user_can_access_protected_view(
    client: Client, user: User
) -> None:
    client.force_login(user)

    response = client.get(reverse("accounts:dashboard"))

    assert response.status_code == 200


def test_unauthenticated_user_can_access_homepage(client: Client) -> None:
    response = client.get(reverse("core:home"))

    assert response.status_code == 200


def test_allauth_login_is_not_blocked_by_global_login_required(client: Client) -> None:
    response = client.get("/auth/login/")

    assert response.status_code == 200


def test_admin_is_not_blocked_by_global_login_required(client: Client) -> None:
    response = client.get("/site-admin/")

    assert response.status_code == 302
    assert "/auth/login/" not in response.headers["Location"]


# TEST NAVBAR BEHAVIOUR
def test_logged_out_navbar_shows_login_and_signup(client: Client) -> None:
    response = client.get(reverse("core:home"))

    assert b'href="/auth/login/"' in response.content
    assert b'href="/auth/signup/"' in response.content


@pytest.mark.django_db
def test_logged_in_navbar_shows_logout(client: Client, user: User) -> None:
    client.force_login(user)

    response = client.get(reverse("core:home"))

    assert b"Log out" in response.content
