from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user_model_create import UserModelCreate
from app.repositories.users_repository_sql import SqlAlchemyUsersRepository


def test_should_create_user_and_return_id_given_payload(tmp_path: Path, monkeypatch):
    # Arrange
    db_file = tmp_path / "repo.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_file}")
    from scripts.seed_users import create_tables  # helper expected in seed script

    create_tables()

    db: Session = SessionLocal()
    repo = SqlAlchemyUsersRepository(db)
    payload = UserModelCreate(login="alice", age=20)

    # Act
    created = repo.create_user(payload)

    # Assert (1 assertion métier)
    assert created.id == 1

    db.close()
