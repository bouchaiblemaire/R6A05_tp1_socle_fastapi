from __future__ import annotations

from app.api.dependencies import get_users_service_dep
from app.services.users_service import UsersService


def test_should_build_users_service_dep():
    # Arrange / Act
    service = get_users_service_dep()

    # Assert (1 assertion métier)
    assert isinstance(service, UsersService)
