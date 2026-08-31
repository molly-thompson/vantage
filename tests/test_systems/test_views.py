from django.test import Client
from django.urls import reverse


def test_systems_index_view(client: Client) -> None:
    response = client.get(reverse("systems:index"))

    assert response.status_code == 200
    assert response.content == b"Systems loads"
