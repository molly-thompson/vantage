from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        ordering = ["-date_joined"]

    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
