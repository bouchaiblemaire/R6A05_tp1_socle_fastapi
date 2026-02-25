
"""
Tests de validation du modèle ORM UserTable.

Objectifs pédagogiques :
- vérifier la clé primaire
- vérifier les colonnes
- vérifier les contraintes structurelles
"""

from sqlalchemy import inspect
from app.models_orm.user_table import UserTable


def test_should_have_users_tablename():
    tablename = UserTable.__tablename__
    assert tablename == "users"


def test_should_have_single_primary_key():
    mapper = inspect(UserTable)
    primary_keys = mapper.primary_key
    assert len(primary_keys) == 1


def test_should_define_id_as_primary_key():
    mapper = inspect(UserTable)
    pk_column = mapper.primary_key[0]
    assert pk_column.name == "id"


def test_should_have_id_not_nullable():
    column = UserTable.__table__.columns["id"]
    assert column.nullable is False


def test_should_have_login_unique_constraint():
    column = UserTable.__table__.columns["login"]
    assert column.unique is True


def test_should_have_correct_column_types():
    columns = UserTable.__table__.columns
    id_type = columns["id"].type.__class__.__name__
    assert id_type == "Integer"
