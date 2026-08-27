from django.urls import reverse


def test_accounts_index_view(client):
    response = client.get(reverse("logs:index"))

    assert response.status_code == 200
    assert response.content == b"Logs loads"
