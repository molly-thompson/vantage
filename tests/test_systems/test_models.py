import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from systems.models import System


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
