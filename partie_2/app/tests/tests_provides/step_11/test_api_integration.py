from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_users_service_dep
from app.factories.users_factory import UsersFactory
from app.repositories.users_repository_fake import FakeUsersRepository
from app.services.users_service import UsersService


@pytest.fixture()
def client(tmp_path: Path):
    # Arrange: deterministic source
    p = tmp_path / "users.json"
    p.write_text(
        json.dumps({"users": [{"id": 1, "login": "alice", "age": 20}, {"id": 2, "login": "bob", "age": 22}]}),
        encoding="utf-8",
    )

    def override_users_service() -> UsersService:
        repo = FakeUsersRepository(factory=UsersFactory(), json_path=str(p))
        return UsersService(repository=repo)

    app.dependency_overrides[get_users_service_dep] = override_users_service
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


def test_should_return_404_given_unknown_user_id(client: TestClient):
    # Arrange
    user_id = 99999

    # Act
    response = client.get(f"/users/{user_id}")

    # Assert (1 assertion métier)
    assert response.status_code == 404


def test_should_return_422_given_invalid_payload(client: TestClient):
    # Arrange
    payload = {"login": "missing_age"}

    # Act
    response = client.post("/users", json=payload)

    # Assert (1 assertion métier)
    assert response.status_code == 422
