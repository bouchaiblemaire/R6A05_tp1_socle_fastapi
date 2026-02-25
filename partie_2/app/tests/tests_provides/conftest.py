from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.settings import get_settings


@pytest.fixture
def client(monkeypatch, tmp_path: Path):
    """
    Fournit un TestClient isolé + configure l'app en profil fake
    avec un JSON de test déterministe (incluant id).
    """

    # 1) Créer un JSON minimal de test (avec id pour éviter ValidationError)
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    users_json = data_dir / "users.json"
    users_json.write_text(
        json.dumps(
            {
                "users": [
                    {"id": 1, "login": "alice", "age": 20},
                    {"id": 2, "login": "bob", "age": 21},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # 2) Forcer le profil + le chemin JSON via variables d'env
    monkeypatch.setenv("APP_PROFILE", "fake")
    monkeypatch.setenv("USERS_JSON_PATH", str(users_json))

    # 3) IMPORTANT : si get_settings() est caché via @lru_cache, il faut vider le cache
    # (sinon il garde l'ancien .env / anciennes vars)
    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()

    # 4) Créer un client propre (lifespan géré)
    with TestClient(app) as c:
        yield c

    # 5) Nettoyage (notamment si d'autres tests override des dépendances)
    app.dependency_overrides.clear()