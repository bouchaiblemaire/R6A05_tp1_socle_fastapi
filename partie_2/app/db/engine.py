from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine, Engine
from app.core.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    """
    Engine = fabrique de connexions.
    On le met en cache (singleton) : OK.
    """
    settings = get_settings()

    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        # utile pour TestClient / threads
        connect_args = {"check_same_thread": False}

    return create_engine(
        settings.database_url,
        echo=True,
        future=True,
        connect_args=connect_args,
    )