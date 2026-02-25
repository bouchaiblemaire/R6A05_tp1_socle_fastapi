from __future__ import annotations

from sqlalchemy import text

from app.db.engine import get_engine


def test_should_execute_select_1_given_engine():
    # Arrange
    engine = get_engine()

    # Act
    with engine.connect() as c:
        result = c.execute(text("SELECT 1")).scalar_one()

    # Assert (1 assertion métier)
    assert result == 1
