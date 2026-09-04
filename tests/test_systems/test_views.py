import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User


@pytest.mark.django_db
def test_systems_index_view(client: Client, user: User) -> None:
    client.force_login(user)
    response = client.get(reverse("systems:index"))

    assert response.status_code == 200
    assert response.content == b"Systems loads"
