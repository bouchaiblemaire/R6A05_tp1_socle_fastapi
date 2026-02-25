from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text

from app.core.settings import get_settings
from app.db.engine import get_engine
from app.db.base import Base
from app.models_orm.user_table import UserTable # Important pour que create_all() puisse mapper UserTable

def main() -> None:
    settings = get_settings()

    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    json_path = Path(settings.users_json_path)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    users_payload = data.get("users") or []

    inserted = 0
    with engine.begin() as conn:
        for u in users_payload:
            conn.execute(
                text("INSERT INTO users (id, login, age) VALUES (:id, :login, :age)"),
                {"id": u["id"], "login": u["login"], "age": u["age"]},
            )
            inserted += 1

    print(f"Inserted: {inserted}")


if __name__ == "__main__":
    main()