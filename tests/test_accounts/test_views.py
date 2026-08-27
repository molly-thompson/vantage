from django.urls import reverse


def test_accounts_index_view(client):
    response = client.get(reverse("accounts:index"))

    assert response.status_code == 200
    assert response.content == b"Accounts loads"
