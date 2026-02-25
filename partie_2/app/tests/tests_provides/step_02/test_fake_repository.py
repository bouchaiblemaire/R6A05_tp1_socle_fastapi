from __future__ import annotations

import json
from pathlib import Path

from app.factories.users_factory import UsersFactory
from app.models.user_model_create import UserModelCreate
from app.repositories.users_repository_fake import FakeUsersRepository


def test_should_list_users_given_json_file(tmp_path: Path):
    # Arrange
    p = tmp_path / "users.json"
    p.write_text(
        json.dumps({"users": [{"id": 1, "login": "alice", "age": 20}, {"id": 2, "login": "bob", "age": 22}]}),
        encoding="utf-8",
    )
    repo = FakeUsersRepository(factory=UsersFactory(), json_path=str(p))

    # Act
    users = repo.list_users()

    # Assert (1 assertion métier)
    assert len(users) == 2


def test_should_return_none_given_unknown_id(tmp_path: Path):
    # Arrange
    p = tmp_path / "users.json"
    p.write_text(json.dumps({"users": [{"id": 1, "login": "alice", "age": 20}]}), encoding="utf-8")
    repo = FakeUsersRepository(factory=UsersFactory(), json_path=str(p))

    # Act
    user = repo.get_user_by_id(999)

    # Assert (1 assertion métier)
    assert user is None


def test_should_create_user_with_incremented_id_given_payload(tmp_path: Path):
    # Arrange
    p = tmp_path / "users.json"
    p.write_text(json.dumps({"users": [{"id": 1, "login": "alice", "age": 20}]}), encoding="utf-8")
    repo = FakeUsersRepository(factory=UsersFactory(), json_path=str(p))
    payload = UserModelCreate(login="bob", age=22)

    # Act
    created = repo.create_user(payload)

    # Assert (1 assertion métier)
    assert created.id == 2
