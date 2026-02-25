from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_should_list_users_given_existing_users(client: TestClient):
    # Arrange
    # fixture client prepared

    # Act
    response = client.get("/users")

    # Assert (1 assertion métier)
    assert len(response.json()) == 2


# ------------------------
# Fixtures (local to step)
# ------------------------

import json
from pathlib import Path
import pytest

from app.api.dependencies import get_users_service_dep
from app.factories.users_factory import UsersFactory
from app.repositories.users_repository_fake import FakeUsersRepository
from app.services.users_service import UsersService


@pytest.fixture()
def client(tmp_path: Path):
    # Arrange: prepare a deterministic JSON source with 2 users
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
