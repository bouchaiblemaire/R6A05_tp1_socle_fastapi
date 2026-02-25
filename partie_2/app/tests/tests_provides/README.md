# Tests fournis — Partie 2 (arborescence par étapes)

Chaque sous-dossier `step_XX/` contient les tests à faire passer pour l’étape.

Lancer une étape :

```bash
pytest tests_provides/step_03
```

## Tableau de correspondance

- `step_01` — UsersFactory (JSON -> UserModel) — `test_users_factory.py`
- `step_02` — FakeUsersRepository (repository fake) — `test_users_repository_fake.py`
- `step_03` — UsersService (logique applicative) — `test_users_service.py`
- `step_04` — API profil fake (TestClient) — `test_users_api.py`
- `step_05` — Settings (.env / valeurs par défaut) — `test_settings.py`
- `step_06` — Composition / dépendances (DI) — `test_dependencies_composition.py`
- `step_07` — Connexion DB (engine/session/get_db) - SELECT 1 — `test_db_connection.py`
- `step_08` — Seed (création tables + remplissage) — `test_seed_users.py`
- `step_09` — Repository SQL (SqlAlchemyUsersRepository) — `test_repository_sql.py`
- `step_10` — API profil SQL — `test_users_api_sql.py`
- `step_11` — Intégration avancée (override dependencies) — (aucun test dans l’archive)
