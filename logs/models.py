from typing import Any, override

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from accounts.models import User
from logs.helpers import get_sentinel_user
from systems.models import ApiEntity


class LogTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def __str__(self) -> str:
        return f"#{self.name}"

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Log(models.Model):
    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Log Entries"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        creator_user__isnull=False,
                        creator_api_entity__isnull=True,
                    )
                    | models.Q(
                        creator_user__isnull=True,
                        creator_api_entity__isnull=False,
                    )
                ),
                name="exactly_one_created_by_type_required",
                violation_error_message="Specify exactly one of "
                "creator_user and creator_api_entity.",
            )
        ]

    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARN", "Warning"
        ERROR = "ERR", "Error"
        CRITICAL = "CRIT", "Critical"

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    body = models.TextField(help_text="Raw log output or Markdown report")
    severity = models.CharField(
        max_length=4, choices=Severity.choices, default=Severity.INFO
    )
    tags = models.ManyToManyField(LogTag, blank=True, related_name="log_entries")
    is_open = models.BooleanField(default=True)
    creator_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET(get_sentinel_user),
        related_name="created_logs",
    )
    creator_api_entity = models.ForeignKey(
        ApiEntity,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="created_logs",
    )

    @override
    def clean(self) -> None:
        super().clean()
        # Python-side check for form and admin validation
        log_creator_user = bool(self.creator_user)
        log_creator_api_entity = bool(self.creator_api_entity)

        if log_creator_user == log_creator_api_entity:
            raise ValidationError(
                "You must provide exactly one of either"
                " creator_user or creator_api_entity."
            )

    def __str__(self) -> str:
        return f"[{self.severity}] {self.title}"


class IncidentNote(models.Model):
    class Meta:
        ordering = ["created_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    log_entry = models.ForeignKey(Log, on_delete=models.CASCADE, related_name="notes")
    creator = models.ForeignKey(
        User,
        on_delete=models.SET(get_sentinel_user),
        null=True,
        blank=True,
        related_name="created_incident_notes",
    )
    content = models.TextField()
    parent_note = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="child_notes",
    )

    def __str__(self) -> str:
        return f"Note by {self.creator}"
