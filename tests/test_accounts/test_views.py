from django.test import Client
from django.urls import reverse


# TESTS FOR PROJECT URL ENDPOINTS
def test_accounts_dashboard_view(client: Client) -> None:
    response = client.get(reverse("accounts:dashboard"))

    assert response.status_code == 200
    assert response.content == b"Accounts dashboard loads"


# TEST ALLAUTH URLS ARE CORRECTLY WIRED INTO PROJECT
def test_allauth_login_url_is_wired(client: Client) -> None:
    response = client.get(reverse("account_login"))

    assert response.status_code == 200
    content = response.content.decode()
    assert content.count("<!DOCTYPE html>") == 1
    assert "Vantage" in content
    title = content.split("<title>", 1)[1].split("</title>", 1)[0]
    assert "Sign In" in title
    assert "Sign In" in content


def test_allauth_signup_url_is_wired(client: Client) -> None:
    response = client.get(reverse("account_signup"))

    assert response.status_code == 200


def test_allauth_logout_url_is_wired(client: Client) -> None:
    response = client.get(reverse("account_logout"))

    assert response.status_code == 302
