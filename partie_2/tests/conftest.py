from __future__ import annotations

"""
conftest.py — Fixtures partagées pour la Partie 2 (SQLAlchemy + SQLite)

Objectif général
----------------
Fournir aux tests une base SQLite *isolée* et *reproductible* :

- une DATABASE_URL temporaire (un fichier SQLite par test)
- un Engine SQLAlchemy créé à partir de cette URL
- les tables créées (Base.metadata.create_all)
- une Session SQLAlchemy (transaction / unité de travail) fournie au test

Point clé : gestion des caches
------------------------------
Dans le TP, on met souvent @lru_cache sur :
- get_settings()
- get_engine() (via une fonction interne _cached_engine)

Cela améliore les performances en prod, mais en test on modifie l'environnement
(DATABASE_URL, USERS_JSON_PATH, APP_PROFILE, etc.). Si on ne vide pas les caches,
les tests peuvent réutiliser l'ancienne configuration / l'ancien Engine.

=> On fournit donc clear_caches() et on l'appelle après chaque setenv important.
"""

import json
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings
from app.db.base import Base

# IMPORTANT :
# Base.metadata.create_all() ne crée les tables que si "Base connaît" vos modèles ORM.
# On importe donc UserTable pour enregistrer la table dans le metadata.
from app.models_orm.user_table import UserTable  # noqa: F401

from app.db.engine import get_engine, _cached_engine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clear_caches() -> None:
    """
    Vide les caches LRU utilisés par l'application.

    Quand l'utiliser ?
    - après un monkeypatch.setenv(...) sur DATABASE_URL / USERS_JSON_PATH / APP_PROFILE
    - avant d'appeler get_settings() et get_engine()

    Pourquoi ?
    - get_settings() peut être décoré avec @lru_cache => garde en mémoire l'ancienne config
    - _cached_engine() peut être décoré avec @lru_cache => garde en mémoire l'ancien Engine

    Sans cache_clear() :
    - les tests peuvent pointer vers la mauvaise base
    - les tests d'anti-régression deviennent non reproductibles
    """
    get_settings.cache_clear()
    _cached_engine.cache_clear()


# ---------------------------------------------------------------------------
# 1) Préparation un environnement complet pour les tests de seed.
# ---------------------------------------------------------------------------


@pytest.fixture
def seed_env(tmp_path: Path, monkeypatch) -> Path:
    """
    Prépare un environnement complet pour les tests de seed.

    Objectif :
    - Créer un fichier JSON temporaire contenant des utilisateurs
    - Créer une base SQLite temporaire
    - Configurer les variables d'environnement nécessaires
    - Vider les caches (Settings + Engine)

    Cette fixture garantit :
    - Isolation totale entre les tests
    - Aucune dépendance à data/app.db
    - Reproductibilité des tests

    Paramètres pytest injectés :
    - tmp_path :
        Dossier temporaire unique pour le test courant.
        Permet de créer des fichiers isolés.

    - monkeypatch :
        Permet de modifier temporairement les variables
        d'environnement (ex: DATABASE_URL, USERS_JSON_PATH).

    Étapes réalisées :

    1) Création du fichier JSON temporaire
    2) Création d’un chemin SQLite temporaire
    3) Configuration des variables d'environnement
    4) Réinitialisation des caches LRU
    5) Retour du chemin de base pour vérification

    Retour :
        Path du fichier SQLite temporaire
    """

    # ---------------------------
    # 1) Création JSON temporaire
    # ---------------------------
    json_path = tmp_path / "users.json"
    json_path.write_text(
        json.dumps({
            "users": [
                {"id": 1, "login": "alice", "age": 20},
                {"id": 2, "login": "bob", "age": 22},
            ]
        }),
        encoding="utf-8",
    )

    # ---------------------------
    # 2) Création DB temporaire
    # ---------------------------
    db_file = tmp_path / "test_app.db"

    # ---------------------------
    # 3) Injection variables env
    # ---------------------------
    monkeypatch.setenv(
        "DATABASE_URL",
        f"sqlite+pysqlite:///{db_file}"
    )

    monkeypatch.setenv(
        "USERS_JSON_PATH",
        str(json_path)
    )

    # --------------------------------
    # 4) Vider les caches LRU
    # --------------------------------
    # Si on ne fait pas cela :
    # - get_settings() peut rester figé
    # - _cached_engine() peut garder l'ancien Engine
    get_settings.cache_clear()
    _cached_engine.cache_clear()

    # --------------------------------
    # 5) Retour du chemin DB
    # --------------------------------
    return db_file


# ---------------------------------------------------------------------------
# 2) Configuration temporaire : DATABASE_URL (un fichier SQLite par test)
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_db_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """
    Fournit une DATABASE_URL unique par test.

    Ce que fait cette fixture :
    1) Crée un fichier SQLite temporaire : <tmp_path>/app.db
    2) Définit DATABASE_URL pour le test (monkeypatch.setenv)
    3) Vide les caches pour forcer l'application à relire la config
    4) Retourne l'URL, utile si un test veut l'afficher/logguer

    Remarque :
    - tmp_path est fourni par pytest : un dossier temporaire différent par test.
    - monkeypatch modifie l'environnement *uniquement pendant le test*.
    """
    db_file = tmp_path / "app.db"
    url = f"sqlite+pysqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", url)

    # Important : on force la relecture de Settings + Engine après modification de l'env.
    clear_caches()
    return url


@pytest.fixture
def temp_users_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Crée un fichier users.json temporaire et configure USERS_JSON_PATH.

    Utilité :
    - certains tests (seed, factory fake...) ont besoin d'une source JSON stable
    - on évite de dépendre de data/users.json (qui peut être modifié localement)

    Remarque :
    - on ne vide pas systématiquement les caches ici : faites-le si vos Settings
      mettent en cache USERS_JSON_PATH.
    """
    json_path = tmp_path / "users.json"
    json_path.write_text(
        json.dumps(
            {
                "users": [
                    {"id": 1, "login": "alice", "age": 20},
                    {"id": 2, "login": "bob", "age": 22},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("USERS_JSON_PATH", str(json_path))

    # Si get_settings() est en cache et lit USERS_JSON_PATH, on force la relecture.
    clear_caches()
    return json_path


# ---------------------------------------------------------------------------
# 3) Engine SQLAlchemy (dépend de temp_db_url)
# ---------------------------------------------------------------------------

@pytest.fixture
def engine(temp_db_url: str) -> Engine:
    """
    Fournit un Engine SQLAlchemy prêt à l'emploi.

    Dépendance :
    - temp_db_url : garantit que DATABASE_URL pointe vers une base isolée.

    Ce que fait la fixture :
    1) appelle get_engine() (qui lit Settings.database_url)
    2) crée les tables via Base.metadata.create_all(engine)
    3) retourne l'Engine au test

    Pourquoi create_all ici ?
    - pour que les tests puissent exécuter des requêtes sans Alembic
    - pour que le seed/repository puisse insérer des lignes immédiatement
    """
    eng = get_engine()
    Base.metadata.create_all(eng)
    return eng


# ---------------------------------------------------------------------------
# 4) Session SQLAlchemy (dépend de engine)
# ---------------------------------------------------------------------------

@pytest.fixture
def db(engine: Engine) -> Generator[Session, None, None]:
    """
    Fournit une Session SQLAlchemy (unité de travail) isolée par test.

    Cycle de vie (pytest) :
    - le code AVANT yield s'exécute avant le test
    - yield donne la Session au test
    - le code APRÈS yield s'exécute après le test (cleanup)

    Pourquoi un generator ?
    - pour garantir session.close() même si le test échoue

    Remarque importante :
    - On NE met PAS la Session en cache (@lru_cache interdit ici).
      Une Session est courte, locale, et doit être fermée.
    """
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

