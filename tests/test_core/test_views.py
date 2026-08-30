from django.test import Client
from django.urls import reverse


def test_core_index_view(client: Client) -> None:
    response = client.get(reverse("core:index"))

    assert response.status_code == 200
    assert "base.html" in [template.name for template in response.templates]
