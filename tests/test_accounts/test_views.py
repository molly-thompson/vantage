from django.test import Client
from django.urls import reverse


# TESTS FOR PROJECT URL ENDPOINTS
def test_accounts_dashboard_view(client: Client) -> None:
    response = client.get(reverse("accounts:dashboard"))

    assert response.status_code == 200
    assert response.content == b"Accounts dashboard loads"
