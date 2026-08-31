from django.db import models

from accounts.models import User


class System(models.Model):
    class Meta:
        ordering = ["-created_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=60)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_systems"
    )
    members = models.ManyToManyField(User, related_name="systems")
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"System {self.name}, owned by {self.owner}"
