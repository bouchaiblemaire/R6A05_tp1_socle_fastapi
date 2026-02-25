from __future__ import annotations

from sqlalchemy.orm import Session

from app.api.dependencies import build_users_repository, get_users_service
from app.repositories.users_repository_fake import FakeUsersRepository
from app.repositories.users_repository_sql import UsersRepositorySql
from app.services.users_service import UsersService


class StubSettings:
    """
    Stub de Settings pour piloter users_backend en test,
    sans dépendre de .env / get_settings().
    """

    def __init__(self, users_backend: str, users_json_path: str = "data/users.json") -> None:
        self.users_backend = users_backend
        self.users_json_path = users_json_path


class StubSession(Session):
    """
    Stub minimal de Session.
    On ne l'utilise pas vraiment en 'db' ici, on vérifie juste le câblage.
    """
    pass


def test_should_build_fake_repository_given_fake_backend():
    # Arrange
    settings = StubSettings(users_backend="fake")

    # Act
    repo = build_users_repository(settings=settings, db=None)

    # Assert (1 assertion métier)
    assert isinstance(repo, FakeUsersRepository)


def test_should_build_sql_repository_given_db_backend_and_session():
    # Arrange
    settings = StubSettings(users_backend="db")
    db = StubSession()

    # Act
    repo = build_users_repository(settings=settings, db=db)

    # Assert (1 assertion métier)
    assert isinstance(repo, UsersRepositorySql)


def test_should_raise_runtime_error_given_db_backend_and_missing_session():
    # Arrange
    settings = StubSettings(users_backend="db")

    # Act / Assert (1 assertion métier)
    try:
        build_users_repository(settings=settings, db=None)
        assert False  # ne doit pas arriver
    except RuntimeError:
        assert True


def test_should_build_users_service_given_dependencies_are_provided():
    # Arrange
    settings = StubSettings(users_backend="fake")
    db = StubSession()

    # Act
    service = get_users_service(settings=settings, db=db)

    # Assert (1 assertion métier)
    assert isinstance(service, UsersService)