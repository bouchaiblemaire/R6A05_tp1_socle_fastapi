# README — conftest.py (Partie 2 : SQLAlchemy + TDD)

Ce document explique **comment** et **quand** les fixtures de `conftest.py` sont utilisées pendant l’exécution des tests.

---

## 1) Comment pytest choisit les fixtures ?

Pytest lit la **signature** d’un test :

```python
def test_something(db):
    ...
```

Ici, `db` est une fixture : pytest doit la construire **avant** d’exécuter le test.

Ensuite, pytest regarde les dépendances de `db` :

- `db(engine)`
- `engine(temp_db_url)`
- `temp_db_url(tmp_path, monkeypatch)`

Pytest construit donc un **graphe de dépendances** et exécute dans l’ordre nécessaire.

---

## 2) L’ordre typique d’exécution

Si un test demande `db`, l’ordre est généralement :

1. `temp_db_url`  
2. `engine`  
3. `db`  
4. exécution du test  
5. teardown de `db` (après `yield`)  
6. (éventuellement teardown d’autres fixtures)

Représentation :

```text
TEST démarre
  |
  |-- temp_db_url (setenv DATABASE_URL + clear_caches)
  |
  |-- engine (get_engine + create_all)
  |
  |-- db (ouvre session + yield)
  |
  |-- exécution du test
  |
  |-- db teardown (session.close)
FIN
```

---

## 3) Pourquoi `temp_db_url` est indispensable ?

Sans base temporaire, vos tests risquent de :

- partager une base `data/app.db` locale,
- accumuler des données entre tests,
- devenir non reproductibles (anti-régression instable).

Avec `temp_db_url` :

- **chaque test** obtient son propre `app.db` dans `tmp_path`,
- les tests sont isolés et répétables.

---

## 4) Pourquoi `clear_caches()` ?

Dans le TP, on met souvent `@lru_cache` sur :

- `get_settings()` (configuration)
- un cache d’engine type `_cached_engine()` (Engine SQLAlchemy)

Si un test fait :

```python
monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///...")
```

mais que `get_settings()` est déjà en cache, alors :

- Settings ne relit pas l’environnement,
- l’Engine peut rester celui de l’ancienne base,
- le test pointe vers la mauvaise base.

`clear_caches()` force la reconstruction :

- `get_settings.cache_clear()`
- `_cached_engine.cache_clear()`

---

## 5) Où mettre `temp_db_url` dans les tests ?

Deux approches :

### A) Le test utilise `db`
La plus fréquente. Exemple :

```python
def test_should_insert_user(db):
    ...
```

Ici, `db` dépend déjà de `engine`, qui dépend de `temp_db_url`.  
Vous n’avez rien à ajouter dans la signature.

### B) Le test a besoin de l’URL
Exemple (test de seed, debug) :

```python
def test_seed_script(temp_db_url, temp_users_json):
    from app.scripts.seed_users import main
    main()
```

Ici, le test utilise explicitement `temp_db_url` et/ou `temp_users_json`.

---

## 6) Rappel : `tmp_path` et `monkeypatch`

- `tmp_path` : dossier temporaire **unique** (créé par pytest)  
  Exemple : `tmp_path / "users.json"` fabrique un chemin vers un fichier dans ce dossier.

- `monkeypatch` : outil pytest pour modifier :
  - variables d’environnement (`setenv`, `delenv`)
  - attributs / fonctions pendant le test

Ces modifications sont automatiquement annulées après le test.

---

## 7) Bonnes pratiques

- Ne jamais utiliser `@lru_cache` sur une **Session**.
- Toujours isoler la base en test (tmp_path).
- Toujours vider les caches après modification de l’environnement.
- Garder **1 assertion métier** par test (comme demandé dans le TP).

---

## 8) Mini FAQ

### Pourquoi `engine` dépend de `temp_db_url` alors qu’il n’utilise pas la variable ?
Parce que `get_engine()` lit `DATABASE_URL` via `Settings`.  
La dépendance garantit que `DATABASE_URL` est déjà correctement configurée.

### Pourquoi importer `UserTable` dans `conftest.py` ?
Pour que `Base.metadata` connaisse la table `users` au moment de `create_all()`.  
Sans cet import, `create_all()` peut ne créer aucune table.

