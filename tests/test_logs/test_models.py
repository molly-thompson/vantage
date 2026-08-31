import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from accounts.models import User
from logs.models import Log, LogTag
from systems.models import ApiEntity, System

# TESTS FOR LOG MODEL


@pytest.mark.django_db
def test_log_can_be_created_by_user(user: User, system: System) -> None:
    log = Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_user=user,
    )

    assert log.title == "Test Log"
    assert log.body == "Test log body"
    assert log.creator_user == user
    assert log.creator_api_entity is None
    assert log.created_at is not None


@pytest.mark.django_db
def test_log_can_be_created_by_api_entity(
    system: System,
    api_entity: ApiEntity,
) -> None:
    log = Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_api_entity=api_entity,
    )

    assert log.creator_api_entity == api_entity
    assert log.creator_user is None


@pytest.mark.django_db
def test_log_defaults_to_info_severity(user: User) -> None:
    log = Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_user=user,
    )

    assert log.severity == Log.Severity.INFO


@pytest.mark.django_db
def test_log_defaults_to_open(user: User) -> None:
    log = Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_user=user,
    )

    assert log.is_open is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "severity",
    [
        Log.Severity.INFO,
        Log.Severity.WARNING,
        Log.Severity.ERROR,
        Log.Severity.CRITICAL,
    ],
)
def test_log_accepts_valid_severity(user: User, severity: Log.Severity) -> None:
    log = Log(
        title="Test Log",
        body="Test log body",
        severity=severity,
        creator_user=user,
    )

    log.full_clean()

    assert log.severity == severity


@pytest.mark.django_db
def test_log_requires_title(user: User) -> None:
    log = Log(
        body="Test log body",
        creator_user=user,
    )

    with pytest.raises(ValidationError):
        log.full_clean()


@pytest.mark.django_db
def test_log_requires_body(user: User) -> None:
    log = Log(
        title="Test Log",
        creator_user=user,
    )

    with pytest.raises(ValidationError):
        log.full_clean()


@pytest.mark.django_db
def test_log_requires_creator() -> None:
    log = Log(
        title="Test Log",
        body="Test log body",
    )

    with pytest.raises(ValidationError):
        log.full_clean()


@pytest.mark.django_db
def test_log_cannot_have_both_creator_types(user: User, api_entity: ApiEntity) -> None:
    log = Log(
        title="Test Log",
        body="Test log body",
        creator_user=user,
        creator_api_entity=api_entity,
    )

    with pytest.raises(ValidationError):
        log.full_clean()


@pytest.mark.django_db
def test_database_rejects_log_without_creator() -> None:
    with pytest.raises(IntegrityError):
        Log.objects.create(
            title="Test Log",
            body="Test log body",
        )


@pytest.mark.django_db
def test_database_rejects_log_with_both_creator_types(
    user: User,
    api_entity: ApiEntity,
    system: System,
) -> None:
    with pytest.raises(IntegrityError):
        Log.objects.create(
            title="Test Log",
            body="Test log body",
            creator_user=user,
            creator_api_entity=api_entity,
        )


@pytest.mark.django_db
def test_user_created_logs_relationship(user: User) -> None:
    log = Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_user=user,
    )

    assert list(user.created_logs.all()) == [log]


@pytest.mark.django_db
def test_api_entity_created_logs_relationship(
    api_entity: ApiEntity,
    system: System,
) -> None:
    log = Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_api_entity=api_entity,
    )

    assert list(api_entity.created_logs.all()) == [log]


@pytest.mark.django_db
def test_log_can_have_multiple_tags(user: User) -> None:
    performance = LogTag.objects.create(name="performance")
    database = LogTag.objects.create(name="database")

    log = Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_user=user,
    )
    log.tags.add(performance, database)

    assert set(log.tags.all()) == {performance, database}
    assert set(performance.log_entries.all()) == {log}
    assert set(database.log_entries.all()) == {log}


@pytest.mark.django_db
def test_log_tags_are_optional(log: Log) -> None:
    assert not log.tags.exists()


@pytest.mark.django_db
def test_deleting_user_replaces_log_creator_with_sentinel_user(
    user: User,
    log: Log,
) -> None:
    user.delete()
    log.refresh_from_db()

    sentinel_user = log.creator_user

    assert sentinel_user is not None
    assert sentinel_user.email == "deleted@vantage.invalid"
    assert sentinel_user.first_name == "Deleted"
    assert sentinel_user.last_name == "User"


@pytest.mark.django_db
def test_deleting_api_entity_is_protected(
    api_entity: ApiEntity, system: System
) -> None:
    log = Log.objects.create(
        title="Test Log",
        body="Test log body",
        creator_api_entity=api_entity,
    )

    with pytest.raises(ProtectedError):
        api_entity.delete()

    assert Log.objects.filter(pk=log.pk).exists()
    assert ApiEntity.objects.filter(pk=api_entity.pk).exists()


@pytest.mark.django_db
def test_log_str(user: User) -> None:
    log = Log.objects.create(
        title="Database connection failed",
        body="Connection refused.",
        severity=Log.Severity.ERROR,
        creator_user=user,
    )

    assert str(log) == "[ERR] Database connection failed"


@pytest.mark.django_db
def test_log_ordering(user: User) -> None:
    older_log = Log.objects.create(
        title="Older Log",
        body="Older log body",
        creator_user=user,
    )
    newer_log = Log.objects.create(
        title="Newer Log",
        body="Newer log body",
        creator_user=user,
    )

    assert list(Log.objects.all()) == [newer_log, older_log]
