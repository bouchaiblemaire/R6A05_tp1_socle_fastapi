from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine, Engine
from app.core.settings import get_settings


@lru_cache
def _cached_engine(database_url: str) -> Engine:
    """
    Fabrique et met en cache un Engine SQLAlchemy pour une URL donnée.

    Pourquoi mettre en cache ?

    - La création d’un Engine est coûteuse (initialisation du pool, configuration interne).
    - En application web, l’Engine est conçu pour être partagé (thread-safe).
    - On veut un seul Engine par base de données.

    Pourquoi le cache dépend-il de l’URL ?

    - En tests, on peut changer DATABASE_URL dynamiquement (monkeypatch).
    - Si on ne dépendait pas de l’URL, le cache figerait l’Engine
      et les tests utiliseraient la mauvaise base.
    - Ici, chaque URL possède son propre Engine en cache.
    """
    return create_engine(database_url, future=True)

def get_engine(database_url: str | None = None)-> Engine:
    """
    Retourne un Engine SQLAlchemy prêt à être utilisé.

    Comportement :

    - Si `database_url` est fourni :
        → on crée (ou récupère en cache) un Engine pour cette URL.
        → utile dans les scripts ou les tests.

    - Si `database_url` est None :
        → on lit l’URL depuis la configuration (`get_settings()`).
        → comportement standard en application FastAPI.

    Important :

    - L’Engine représente une fabrique de connexions (pas une connexion active).
    - Il est thread-safe et doit être partagé.
    - Il ne faut PAS créer un Engine par requête.
    - La Session, en revanche, ne doit jamais être mise en cache.

    En résumé :
        Engine = singleton par base de données.
        Session = unité de travail, créée dynamiquement.
    """
    if database_url is None:
        database_url = get_settings().database_url

    return _cached_engine(database_url)