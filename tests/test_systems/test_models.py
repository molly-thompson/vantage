import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from systems.models import ApiEntity, System


@pytest.mark.django_db
def test_system_can_be_created() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )

    system = System.objects.create(
        name="Test System",
        owner=owner,
        description="A test system.",
    )

    assert system.name == "Test System"
    assert system.owner == owner
    assert system.description == "A test system."
    assert system.created_at is not None


@pytest.mark.django_db
def test_system_requires_name() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )

    system = System(
        owner=owner,
    )

    with pytest.raises(ValidationError):
        system.full_clean()


@pytest.mark.django_db
def test_system_requires_owner() -> None:
    system = System(
        name="Test System",
    )

    with pytest.raises(ValidationError):
        system.full_clean()


@pytest.mark.django_db
def test_system_description_is_optional() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )

    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    assert system.description == ""


@pytest.mark.django_db
def test_system_owner_relationship() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )

    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    assert system.owner == owner
    assert list(owner.owned_systems.all()) == [system]


@pytest.mark.django_db
def test_system_members_can_be_added() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    member = User.objects.create_user(
        username="member",
        email="member@example.com",
        password="password123",
    )

    system = System.objects.create(
        name="Test System",
        owner=owner,
    )
    system.members.add(member)

    assert list(system.members.all()) == [member]
    assert list(member.systems.all()) == [system]


@pytest.mark.django_db
def test_system_can_have_multiple_members() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    member_one = User.objects.create_user(
        username="member1",
        email="one@example.com",
        password="password123",
    )
    member_two = User.objects.create_user(
        username="member2",
        email="two@example.com",
        password="password123",
    )

    system = System.objects.create(
        name="Test System",
        owner=owner,
    )
    system.members.add(member_one, member_two)

    assert system.members.count() == 2
    assert set(system.members.all()) == {member_one, member_two}


@pytest.mark.django_db
def test_system_owner_can_also_be_a_member() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )

    system = System.objects.create(
        name="Test System",
        owner=owner,
    )
    system.members.add(owner)

    assert system.members.filter(pk=owner.pk).exists()


@pytest.mark.django_db
def test_deleting_owner_deletes_system() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    system_id = system.pk
    owner.delete()

    assert not System.objects.filter(pk=system_id).exists()


@pytest.mark.django_db
def test_deleting_member_does_not_delete_system() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    member = User.objects.create_user(
        username="member",
        email="member@example.com",
        password="password123",
    )

    system = System.objects.create(
        name="Test System",
        owner=owner,
    )
    system.members.add(member)

    member.delete()

    assert System.objects.filter(pk=system.pk).exists()


@pytest.mark.django_db
def test_system_str() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
        first_name="Test",
        last_name="Owner",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    assert str(system) == "System Test System, owned by Test Owner"


@pytest.mark.django_db
def test_system_ordering() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )

    older_system = System.objects.create(
        name="Older System",
        owner=owner,
    )
    newer_system = System.objects.create(
        name="Newer System",
        owner=owner,
    )

    assert list(System.objects.all()) == [newer_system, older_system]


# TESTS FOR API ENTITY


@pytest.mark.django_db
def test_api_entity_can_be_created() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    api_entity = ApiEntity.objects.create(
        system=system,
        name="PostsAPI",
        key_hash="test-key-hash",
    )

    assert api_entity.system == system
    assert api_entity.name == "PostsAPI"
    assert api_entity.key_hash == "test-key-hash"
    assert api_entity.key_created is not None
    assert api_entity.created_at is not None
    assert api_entity.api_key_stale is False


@pytest.mark.django_db
def test_api_entity_requires_system() -> None:
    api_entity = ApiEntity(
        name="PostsAPI",
        key_hash="test-key-hash",
    )

    with pytest.raises(ValidationError):
        api_entity.full_clean()


@pytest.mark.django_db
def test_api_entity_requires_name() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    api_entity = ApiEntity(
        system=system,
        key_hash="test-key-hash",
    )

    with pytest.raises(ValidationError):
        api_entity.full_clean()


@pytest.mark.django_db
def test_api_entity_requires_key_hash() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    api_entity = ApiEntity(
        system=system,
        name="PostsAPI",
    )

    with pytest.raises(ValidationError):
        api_entity.full_clean()


@pytest.mark.django_db
def test_api_entity_belongs_to_system() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )
    api_entity = ApiEntity.objects.create(
        system=system,
        name="PostsAPI",
        key_hash="test-key-hash",
    )

    assert api_entity.system == system
    assert list(system.api_entities.all()) == [api_entity]


@pytest.mark.django_db
def test_system_can_have_multiple_api_entities() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    posts_api = ApiEntity.objects.create(
        system=system,
        name="PostsAPI",
        key_hash="posts-key-hash",
    )
    users_api = ApiEntity.objects.create(
        system=system,
        name="UsersAPI",
        key_hash="users-key-hash",
    )

    assert system.api_entities.count() == 2
    assert set(system.api_entities.all()) == {posts_api, users_api}


@pytest.mark.django_db
def test_api_entity_defaults_to_not_stale() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    api_entity = ApiEntity.objects.create(
        system=system,
        name="PostsAPI",
        key_hash="test-key-hash",
    )

    assert api_entity.api_key_stale is False


@pytest.mark.django_db
def test_deleting_system_deletes_api_entities() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )
    api_entity = ApiEntity.objects.create(
        system=system,
        name="PostsAPI",
        key_hash="test-key-hash",
    )

    api_entity_id = api_entity.pk
    system.delete()

    assert not ApiEntity.objects.filter(pk=api_entity_id).exists()


@pytest.mark.django_db
def test_api_entity_str() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )
    api_entity = ApiEntity.objects.create(
        system=system,
        name="PostsAPI",
        key_hash="test-key-hash",
    )

    assert str(api_entity) == "API Entity PostsAPI, belonging to system Test System"


@pytest.mark.django_db
def test_api_entity_ordering() -> None:
    owner = User.objects.create_user(
        username="testuser",
        email="owner@example.com",
        password="password123",
    )
    system = System.objects.create(
        name="Test System",
        owner=owner,
    )

    older_entity = ApiEntity.objects.create(
        system=system,
        name="OlderAPI",
        key_hash="older-key-hash",
    )
    newer_entity = ApiEntity.objects.create(
        system=system,
        name="NewerAPI",
        key_hash="newer-key-hash",
    )

    assert list(ApiEntity.objects.all()) == [newer_entity, older_entity]
