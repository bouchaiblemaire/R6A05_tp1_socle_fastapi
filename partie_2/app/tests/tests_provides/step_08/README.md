# step_08


Test fourni : `test_sql_repository.py`

Commande :

```bash
pytest tests_provides/step_08
```


# README — Tests Step 08 (SqlAlchemyUsersRepository)

## Objectif pédagogique

Ces tests vérifient le bon fonctionnement du repository SQL (`SqlAlchemyUsersRepository`)
et surtout la gestion correcte des contraintes de base de données :

- clé primaire (`id`)
- contrainte `UNIQUE` sur `login`
- gestion des transactions
- isolation des tests

---

## Pourquoi isoler la base de données ?

Si plusieurs tests partagent la même base SQLite :

- des données restent après un test
- des violations de contrainte peuvent apparaître (ex : doublon login)
- les tests deviennent non déterministes

C’est pourquoi nous utilisons une base SQLite temporaire via `tmp_path`.

Chaque test possède :
- son propre fichier `.db`
- son propre Engine
- sa propre Session

Isolation garantie.

---

## Rôle des fixtures pytest

Exemple typique :

```python
@pytest.fixture()
def engine(tmp_path):
    db_path = tmp_path / "test.db"
    return create_engine(f"sqlite+pysqlite:///{db_path}")
```

La fixture :

1. prépare l’environnement
2. injecte la dépendance dans le test
3. nettoie automatiquement après exécution

Cela fonctionne comme une injection de dépendance côté tests.

---

## Ce que vérifient les tests

### 1. Création utilisateur valide

- insertion correcte
- génération automatique de l'id
- commit effectué

### 2. Doublon `login`

- tentative d'insertion avec login déjà existant
- levée d'une `IntegrityError`

### 3. Contrainte clé primaire

- vérifie que `id` est bien `primary_key=True`

---

## Architecture traversée dans les tests

```text
Test
   |
Repository SQL
   |
Session
   |
Engine
   |
SQLite temporaire
```

---

## Message clé

Un test SQL fiable doit :

- utiliser une base isolée
- ne jamais dépendre d’un état précédent
- vérifier explicitement les contraintes
- rester déterministe

---

## À retenir

Ces tests valident :

- la couche Repository
- l'intégration ORM
- la gestion des contraintes SQL
- la qualité architecturale

Ils sont essentiels pour garantir la robustesse de la Partie 2.
