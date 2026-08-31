from accounts.models import User


def get_sentinel_user() -> User:
    return User.objects.get_or_create(
        email="deleted@vantage.invalid",
        defaults={
            "first_name": "Deleted",
            "last_name": "User",
        },
    )[0]
