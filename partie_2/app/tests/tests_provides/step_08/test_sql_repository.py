from __future__ import annotations

import uuid
from pathlib import Path

import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_model_create import UserModelCreate
from app.models_orm.user_table import UserTable
from app.repositories.users_repository_sql import UsersRepositorySql



def _unique_login(prefix: str = "user") -> str:
    """
    Helper de test : génère un login unique pour éviter les collisions
    involontaires avec la contrainte UNIQUE.
    """
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_should_create_user_and_return_id_given_payload(db: Session):
    # Arrange
    repo = UsersRepositorySql(db)
    payload = UserModelCreate(login=_unique_login("alice"), age=20)

    # Act
    created = repo.create_user(payload)

    # Assert (1 assertion métier)
    assert created.id >= 1


def test_should_raise_integrity_error_given_duplicate_login(db: Session):
    # Arrange
    repo = UsersRepositorySql(db)
    login = _unique_login("dup")
    payload1 = UserModelCreate(login=login, age=20)
    payload2 = UserModelCreate(login=login, age=21)

    # Act
    repo.create_user(payload1)

    # Assert (1 assertion métier)
    with pytest.raises(IntegrityError):
        repo.create_user(payload2)


def test_should_create_distinct_ids_given_two_creations(db: Session):
    # Arrange
    repo = UsersRepositorySql(db)
    p1 = UserModelCreate(login=_unique_login("u"), age=20)
    p2 = UserModelCreate(login=_unique_login("u"), age=21)

    # Act
    u1 = repo.create_user(p1)
    u2 = repo.create_user(p2)

    # Assert (1 assertion métier)
    assert u1.id != u2.id


def test_should_reflect_update_given_user_login_modified_in_db(db: Session):
    # Arrange
    repo = UsersRepositorySql(db)
    created = repo.create_user(UserModelCreate(login=_unique_login("before"), age=20))

    new_login = _unique_login("after")

    # Act
    # Update direct via ORM (pédagogique) : on modifie la ligne en base
    stmt = select(UserTable).where(UserTable.id == created.id)
    row = db.execute(stmt).scalar_one()
    row.login = new_login
    db.commit()

    updated = repo.get_user_by_id(created.id)

    # Assert (1 assertion métier)
    assert updated is not None and updated.login == new_login


def test_should_return_none_given_user_deleted_from_db(db: Session):
    # Arrange
    repo = UsersRepositorySql(db)
    created = repo.create_user(UserModelCreate(login=_unique_login("todelete"), age=20))

    # Act
    db.execute(delete(UserTable).where(UserTable.id == created.id))
    db.commit()
    found = repo.get_user_by_id(created.id)

    # Assert (1 assertion métier)
    assert found is None

def test_should_persist_user_in_db_and_find_it_given_created_user(db: Session):
    """
    Vérifie que create_user() écrit réellement en base :
    - on crée un utilisateur
    - on le relit ensuite via get_user_by_id()
    """
    # Arrange
    repo = UsersRepositorySql(db)
    unique_login = f"user_{uuid.uuid4().hex[:8]}"
    payload = UserModelCreate(login=unique_login, age=25)

    # Act
    created = repo.create_user(payload)
    found = repo.get_user_by_id(created.id)

    # Assert (1 assertion métier)
    assert found is not None and found.login == unique_login
