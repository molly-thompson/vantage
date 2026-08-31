import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError, RestrictedError

from accounts.models import User
from logs.models import IncidentNote, Log, LogTag
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


# TESTS FOR INCIDENTNOTE


@pytest.mark.django_db
def test_incident_note_can_be_created(log: Log, user: User) -> None:
    note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Investigating the issue.",
    )

    assert note.log_entry == log
    assert note.creator == user
    assert note.content == "Investigating the issue."
    assert note.parent_note is None
    assert note.created_at is not None


@pytest.mark.django_db
def test_incident_note_requires_log(user: User) -> None:
    note = IncidentNote(
        creator=user,
        content="Investigating the issue.",
    )

    with pytest.raises(ValidationError):
        note.full_clean()


@pytest.mark.django_db
def test_incident_note_creator_is_optional(log: Log) -> None:
    note = IncidentNote.objects.create(
        log_entry=log,
        content="System note.",
    )

    assert note.creator is None


@pytest.mark.django_db
def test_incident_note_content_is_required(log: Log, user: User) -> None:
    note = IncidentNote(
        log_entry=log,
        creator=user,
    )

    with pytest.raises(ValidationError):
        note.full_clean()


@pytest.mark.django_db
def test_log_notes_relationship(log: Log, user: User) -> None:
    note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Investigating the issue.",
    )

    assert list(log.notes.all()) == [note]


@pytest.mark.django_db
def test_user_created_incident_notes_relationship(log: Log, user: User) -> None:
    note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Investigating the issue.",
    )

    assert list(user.created_incident_notes.all()) == [note]


@pytest.mark.django_db
def test_incident_note_can_have_parent(log: Log, user: User) -> None:
    parent_note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Initial investigation.",
    )
    child_note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Following up.",
        parent_note=parent_note,
    )

    assert child_note.parent_note == parent_note
    assert list(parent_note.child_notes.all()) == [child_note]


@pytest.mark.django_db
def test_incident_note_can_have_multiple_children(log: Log, user: User) -> None:
    parent_note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Initial investigation.",
    )
    child_one = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="First follow-up.",
        parent_note=parent_note,
    )
    child_two = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Second follow-up.",
        parent_note=parent_note,
    )

    assert parent_note.child_notes.count() == 2
    assert set(parent_note.child_notes.all()) == {child_one, child_two}


@pytest.mark.django_db
def test_deleting_log_deletes_incident_notes(log: Log, user: User) -> None:
    note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Investigating the issue.",
    )

    note_id = note.pk
    log.delete()

    assert not IncidentNote.objects.filter(pk=note_id).exists()


@pytest.mark.django_db
def test_deleting_user_replaces_note_creator_with_sentinel_user(
    log: Log,
    user: User,
) -> None:
    note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Investigating the issue.",
    )

    user.delete()
    note.refresh_from_db()

    sentinel_user = note.creator

    assert sentinel_user is not None
    assert sentinel_user.email == "deleted@vantage.invalid"
    assert sentinel_user.first_name == "Deleted"
    assert sentinel_user.last_name == "User"


@pytest.mark.django_db
def test_deleting_parent_note_is_restricted(log: Log, user: User) -> None:
    parent_note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Initial investigation.",
    )
    child_note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Follow-up.",
        parent_note=parent_note,
    )

    with pytest.raises(RestrictedError):
        parent_note.delete()

    assert IncidentNote.objects.filter(pk=parent_note.pk).exists()
    assert IncidentNote.objects.filter(pk=child_note.pk).exists()


@pytest.mark.django_db
def test_incident_note_str(log: Log, user: User) -> None:
    note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Investigating the issue.",
    )

    assert str(note) == f"Note by {user}"


@pytest.mark.django_db
def test_incident_note_ordering(log: Log, user: User) -> None:
    older_note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="First note.",
    )
    newer_note = IncidentNote.objects.create(
        log_entry=log,
        creator=user,
        content="Second note.",
    )

    assert list(IncidentNote.objects.all()) == [older_note, newer_note]
