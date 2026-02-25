from __future__ import annotations

from app.models.user_model import UserModel
from app.models.user_model_create import UserModelCreate
from app.services.users_service import UsersService


class StubUsersRepository:
    """Stub minimal pour isoler le service (tests unitaires)."""

    def __init__(self) -> None:
        self._users = [
            UserModel(id=1, login="alice", age=20),
            UserModel(id=2, login="bob", age=22),
        ]

    def list_users(self):
        return self._users

    def get_user_by_id(self, user_id: int):
        return next((u for u in self._users if u.id == user_id), None)

    def create_user(self, payload: UserModelCreate):
        new_id = max(u.id for u in self._users) + 1
        new = UserModel(id=new_id, login=payload.login, age=payload.age)
        self._users.append(new)
        return new


def test_should_list_users_given_initial_users():
    # Arrange
    service = UsersService(repository=StubUsersRepository())

    # Act
    users = service.list_users()

    # Assert (1 assertion métier)
    assert len(users) == 2


def test_should_return_user_given_existing_id():
    # Arrange
    service = UsersService(repository=StubUsersRepository())

    # Act
    user = service.get_user_by_id(1)

    # Assert (1 assertion métier)
    assert user is not None


def test_should_create_user_with_incremented_id_given_payload():
    # Arrange
    service = UsersService(repository=StubUsersRepository())
    payload = UserModelCreate(login="charlie", age=20)

    # Act
    created = service.create_user(payload)

    # Assert (1 assertion métier)
    assert created.id == 3
