import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User


@pytest.mark.django_db
def test_logs_index_view(client: Client, user: User) -> None:
    client.force_login(user)
    response = client.get(reverse("logs:index"))

    assert response.status_code == 200
    assert response.content == b"Logs loads"
