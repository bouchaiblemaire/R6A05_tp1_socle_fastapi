from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db


def test_should_yield_session_given_get_db():
    # Arrange
    gen = get_db()

    # Act
    db = next(gen)

    # Assert (1 assertion métier)
    assert isinstance(db, Session)

    # Cleanup
    gen.close()
