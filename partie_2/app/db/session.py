from __future__ import annotations

from typing import Generator

from anyio.functools import lru_cache
from sqlalchemy.orm import Session, sessionmaker

from app.db.engine import get_engine


# Factory de sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_engine(),
)


def get_db() -> Generator[Session, None, None]:
    """
    Fournit une Session SQLAlchemy et garantit sa fermeture.

    Returns:
        Generator[Session, None, None]: génère une session puis la ferme.

    Notes pédagogiques :
    - la session doit être fermée même en cas d'erreur,
    - ce pattern prépare l'injection via Depends(get_db) en FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()