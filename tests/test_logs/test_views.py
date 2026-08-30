from django.test import Client
from django.urls import reverse


def test_logs_index_view(client: Client) -> None:
    response = client.get(reverse("logs:index"))

    assert response.status_code == 200
    assert response.content == b"Logs loads"
