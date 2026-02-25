from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text

from app.db.engine import get_engine


def test_should_insert_rows_given_seed_script(seed_env: Path):
    # Le parametre seed_env déclenche la fixture seed_env dans le
    # script conftest.py

    # Act
    from app.scripts.seed_users import main  # imported after env set

    main()

    # Assert (1 assertion métier)
    engine = get_engine()
    with engine.connect() as c:
        count = c.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
    assert count == 2
