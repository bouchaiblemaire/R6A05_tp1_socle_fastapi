from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.factories.users_factory import UsersFactory
from app.models.user_model import UserModel


def test_should_create_users_given_valid_users_list(tmp_path: Path):
    # Arrange
    p = tmp_path / "users.json"
    p.write_text(
        json.dumps(
            {"users": [{"id": 1, "login": "alice", "age": 20}, {"id": 2, "login": "bob", "age": 22}]}
        ),
        encoding="utf-8",
    )
    factory = UsersFactory()

    # Act
    users = factory.create_users(str(p))

    # Assert (1 assertion métier)
    assert len(users) == 2


def test_should_raise_value_error_given_users_key_is_missing(tmp_path: Path):
    # Arrange
    p = tmp_path / "users.json"
    p.write_text(json.dumps({"not_users": []}), encoding="utf-8")
    factory = UsersFactory()

    # Act / Assert (1 assertion métier)
    with pytest.raises(ValueError):
        factory.create_users(str(p))


def test_should_raise_value_error_given_users_is_not_a_list(tmp_path: Path):
    # Arrange
    p = tmp_path / "users.json"
    p.write_text(json.dumps({"users": {"id": 1, "login": "alice", "age": 20}}), encoding="utf-8")
    factory = UsersFactory()

    # Act / Assert (1 assertion métier)
    with pytest.raises(ValueError):
        factory.create_users(str(p))
