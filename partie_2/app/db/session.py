from __future__ import annotations

from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings
from app.db.engine import get_engine


def get_sessionmaker():
    """
    Construit dynamiquement un `sessionmaker` basé sur l’Engine courant.

    Pourquoi ne pas le définir au niveau du module ?

    - Si on faisait :
        SessionLocal = sessionmaker(bind=get_engine())
      alors l’Engine serait résolu au moment de l’import.
    - En tests (pytest), on peut modifier DATABASE_URL dynamiquement.
    - Il faut donc éviter de figer le bind trop tôt.

    Cette fonction garantit que :
    - l’Engine est résolu au moment réel de l’appel,
    - les tests utilisant monkeypatch fonctionnent correctement.

    Retour :
        Un objet `sessionmaker` configuré pour créer des Session SQLAlchemy.
    """
    engine = get_engine()
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        future=True,
    )


def get_db() -> Generator[Session, None, None]:
    """
    Fournit une Session SQLAlchemy (unité de travail).

    Rôle dans FastAPI :

    - Ouvre une Session au début de la requête.
    - La rend disponible via `Depends(get_db)`.
    - Garantit sa fermeture en fin de requête.

    Pourquoi utiliser un generator (`yield`) ?

    - `yield` permet à FastAPI de :
        1) récupérer la Session,
        2) exécuter la route,
        3) exécuter le bloc `finally` automatiquement.

    Cycle de vie :

        Requête HTTP
              ↓
        get_db() appelé
              ↓
        Session créée
              ↓
        Route exécutée
              ↓
        finally → session.close()

    Important :

    - Une Session ne doit JAMAIS être mise en cache.
    - Une Session représente une transaction.
    - Elle doit être courte et isolée.

    En résumé :
        Engine  → partagé (singleton par URL)
        Session → créée par requête
    """
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()